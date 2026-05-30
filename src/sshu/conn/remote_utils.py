import typer
import getpass
from pathlib import Path
from fabric import Connection
import paramiko
import sys
import logging
import shutil
from .config_utils import get_sshu_config

logger = logging.getLogger(__name__)

home_dir = Path.home()
ssh_dir = home_dir / ".ssh"
ssh_cfg = ssh_dir / "config"
sshu_marker = "#### Managed by SSHU ####"

def get_server_pubkey(hostname:str, user:str, port:str, retries: int):
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    known_host_string: str = ""
    try:
        logger.info("Connecting to the remote server for pubkey retrieval")
        conn.connect(hostname=hostname, username=user, port=int(port), password="")
    except (paramiko.AuthenticationException, paramiko.SSHException) as auth_err:
        logger.info(f"Auth / Connection restriction bypassed: {type(auth_err).__name__}")
    except Exception as e:
        logger.error(f"Error getting server public key -> {e}")
        typer.secho(f"Error: {type(e).__name__} – {e}", fg=typer.colors.BRIGHT_RED)
        if retries > 0:
            logger.warning(f"Retrying connection to '{hostname}'... {retries} retries left.")
            typer.echo(f"Retrying host [{hostname}] {retries} retries left...")
            get_server_pubkey(hostname,user,port,retries - 1)
        else:
            logger.error(f"Failed to copy pubkey to '{hostname}' after multiple retries.")
            typer.echo(f"host [{hostname}] failed after multiple retries")
            sys.exit()

    trans = conn.get_transport()
    if trans is not None:
        srv_key = trans.get_remote_server_key()  
        srv_key_type = srv_key.get_name()
        srv_key_b64 = srv_key.get_base64()
        known_host_string = f"{hostname} {srv_key_type} {srv_key_b64}\n"
        logger.debug(f"known_host_string -> {known_host_string}")

    with open(f"{ssh_dir}/known_hosts", mode="r") as f:
        tmp_known_hosts_content = f.readlines()

    if known_host_string in tmp_known_hosts_content:
        logger.info("Server public key is already in the known_hosts file")
    else:
        logger.debug("Writing known_host_string to temp file")
        tmp_known_hosts_content.append(known_host_string)
        with open(f"{ssh_dir}/known_hosts_tmp", mode="w") as f:
            f.writelines(tmp_known_hosts_content)
        shutil.copyfile(f"{ssh_dir}/known_hosts_tmp",f"{ssh_dir}/known_hosts")
        logger.debug("Copying temp file into real file")
        logger.info("Server public key successfully injected into known_hosts file")


def copy_pubkey_to_remote(hostname:str, user:str, port:str, retries: int):
    logger.debug(f"Target for pubkey copy -> {user}@{hostname}:{port}")

    cfg_data = get_sshu_config()

    default_identity_file: str = cfg_data["default_identity_key"] + ".pub"

    with open(f"{ssh_dir}/{default_identity_file}", mode="r") as f:
        pubkey = f.read()
    
    password = getpass.getpass("Please enter the ssh user password:") 

    conn = Connection(
        host=hostname,
        user=user,
        port=port,
        connect_kwargs={
            "password": password
        }
    )

    try:
        check_create_ssh_dir = conn.run("mkdir -p $HOME/.ssh && chmod -R 700 $HOME/.ssh", warn=True)
        if check_create_ssh_dir.return_code != 0:
            logger.error("Creating ssh dir failed on remote host.")
            logger.debug(f"Remote STDOUT -> {check_create_ssh_dir.stdout.strip()}")
            logger.debug(f"Remote STDERR -> {check_create_ssh_dir.stderr.strip()}")
            typer.echo("Creating ssh dir failed on remote host")
            typer.echo(f"Remote STDOUT: {check_create_ssh_dir.stdout.strip()}\n\nremote STDERR: {check_create_ssh_dir.stderr.strip()} ")


        check_authorized_keys = conn.run("test -f $HOME/.ssh/authorized_keys", warn=True)
        if check_authorized_keys.return_code != 0:
            create_authorized_keys = conn.run("touch $HOME/.ssh/authorized_keys && chmod 600 $HOME/.ssh/authorized_keys")

            if create_authorized_keys.return_code != 0:
                logger.error("Creating authorized_keys file failed.")
                logger.debug(f"Remote STDOUT -> {create_authorized_keys.stdout.strip()}")
                logger.debug(f"Remote STDERR -> {create_authorized_keys.stderr.strip()}")
                typer.echo("Creating authorized_keys file failed")
                typer.echo(f"Remote STDOUT: {create_authorized_keys.stdout.strip()}\n\nremote STDERR: {create_authorized_keys.stderr.strip()} ")

        check_pub_key = conn.run("cat $HOME/.ssh/authorized_keys" , warn=True, hide=True)
        if pubkey.strip() not in check_pub_key.stdout.strip():
            insert_pub_key = conn.run(f"echo '{pubkey}' >> $HOME/.ssh/authorized_keys", warn=True) 
            if insert_pub_key.return_code != 0:
                logger.error("Inserting pubkey failed.")
                logger.debug(f"Remote STDOUT -> {insert_pub_key.stdout.strip()}")
                logger.debug(f"Remote STDERR -> {insert_pub_key.stderr.strip()}")
                typer.echo("Inserting pubkey failed")
                typer.echo(f"Remote STDOUT: {insert_pub_key.stdout.strip()}\n\nremote STDERR: {insert_pub_key.stderr.strip()} ")
            else:
                logger.info(f"Successfully copied public key to '{hostname}'.")
                typer.echo("Public key copied")
        else:
            logger.info(f"Public key already exists in authorized_keys for '{hostname}'.")
            typer.echo("Pubkey already copied into remote authorized_keys")

    except Exception as e:
        logger.error(f"Error copying pubkey -> {e}")
        typer.secho(f"Error: {type(e).__name__} – {e}", fg=typer.colors.BRIGHT_RED)

        if retries > 0:
            logger.warning(f"Retrying connection to '{hostname}'... {retries} retries left.")
            typer.echo(f"Retrying host [{hostname}] {retries} retries left...")
            copy_pubkey_to_remote(hostname,user,port,retries - 1)
        else:
            logger.error(f"Failed to copy pubkey to '{hostname}' after multiple retries.")
            typer.echo(f"host [{hostname}] failed after multiple retries")
            sys.exit()


def remove_pubkey_from_remote(conn_name:str, ssh_cfg: Path, retries: int):
    logger.debug(f"Target connection for remote pubkey removal -> {conn_name}")
    keyed_line = "#Keyed yes"

    ssh_cfg_content = ssh_cfg.read_text().splitlines()

    host_block_to_delete = []
    
    try:
        conn_name_index = ssh_cfg_content.index("Host " + conn_name)
        for line in ssh_cfg_content[conn_name_index::]:
            if line.startswith('Host ') and conn_name not in line:
                break
            if not line.strip():
                continue
            else:
                host_block_to_delete.append(line.strip())
    except ValueError:
        pass

    if keyed_line not in host_block_to_delete:
        logger.warning(f"Connection '{conn_name}' is not keyed. Aborting remote removal.")
        typer.secho("This connection is not keyed, there is no public key to delete on the remote host...", fg=typer.colors.BRIGHT_RED)
        typer.echo("Please remove the --remote flag to delete the selected connection...")
        sys.exit()
    else:
        host_info = {} 

        for line in host_block_to_delete:
            key, value = line.split()
            host_info[key] = value

        with open(f"{ssh_dir}/id_ed25519.pub", mode="r") as f:
            pubkey = f.read()
        
        conn = Connection(
            host=host_info["HostName"],
            user=host_info["User"],
            port=host_info["Port"]
        )

        try:
            get_authorized_keys = conn.run(f"cat $HOME/.ssh/authorized_keys", hide=True , warn=True)

            if get_authorized_keys.return_code != 0:
                logger.error("Getting the authorized_keys file on remote host failed.")
                logger.debug(f"Remote STDERR -> {get_authorized_keys.stderr.strip()}")
                typer.secho("Getting the authorized_keys file on remote host failed...", fg=typer.colors.BRIGHT_RED)
                typer.secho(f"ERROR - {get_authorized_keys.stderr.strip()}", fg=typer.colors.BRIGHT_RED)
                sys.exit()

            remote_authorized_keys = get_authorized_keys.stdout
            remote_authorized_keys = remote_authorized_keys.replace(pubkey,"").strip()
            update_authorized_keys = conn.run(f"echo '{remote_authorized_keys}' > $HOME/.ssh/authorized_keys", hide=True, warn=True)

            if update_authorized_keys.return_code != 0:
                logger.error("Removing the pubkey from the remote host failed.")
                logger.debug(f"Remote STDERR -> {update_authorized_keys.stderr.strip()}")
                typer.secho("Removing the pubkey from the remote host failed, aborting the remove action...", fg=typer.colors.BRIGHT_RED)
                typer.secho(f"ERROR - {update_authorized_keys.stderr.strip()}", fg=typer.colors.BRIGHT_RED)
                sys.exit()
            logger.info(f"Successfully deleted public key from '{host_info['HostName']}'.")
            typer.echo(f"Public key successfully deleted from {host_info['HostName']}")

        except Exception as e:
            logger.error(f"Error removing pubkey -> {e}")
            typer.secho(f"Error: {type(e).__name__} – {e}", fg=typer.colors.BRIGHT_RED)
            
            if retries > 0:
                confirmation: str = ""
                while confirmation not in ("y","n"):
                    confirmation = input("Retry? Y/n: ").strip().lower() or "y"
                if confirmation == "n":
                    logger.info("User aborted retry for remote pubkey removal.")
                    sys.exit()
                elif confirmation == "y":
                    logger.warning(f"Retrying pubkey removal from '{host_info['HostName']}'... {retries} retries left.")
                    typer.echo(f"Retrying pubkey removal from [{host_info['HostName']}] {retries} retries left... ")
                    remove_pubkey_from_remote(conn_name, ssh_cfg, retries -1)
            else:
                logger.error(f"Failed to remove pubkey from '{host_info['HostName']}' after multiple retries.")
                typer.echo(f"host [{host_info['HostName']}] failed after multiple retries")
                sys.exit()
