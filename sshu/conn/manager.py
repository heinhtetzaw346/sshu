import typer
import getpass
from pathlib import Path
from rich.table import Table
from rich.console import Console
from fabric import Connection
import sys

home_dir = Path.home()
ssh_dir = home_dir / ".ssh"
ssh_cfg = ssh_dir / "config"
sshu_marker = "#### Managed by SSHU ####"


def add(address_string: str, conn_name: str, passwd: bool, copyid: bool, keypair: str, port: str):

    ssh_cfg_content = ssh_cfg.read_text().splitlines()

    if conn_name_exists(conn_name, ssh_cfg_content):
        typer.secho(f"Connection {conn_name} already exists", fg=typer.colors.BRIGHT_RED)
        sys.exit()

    user,hostname = address_string.split('@')
    host_cfg = f"Host {conn_name}\n  HostName {hostname}\n  User {user}\n  Port {port}\n"
    ssh_cfg_content = ssh_cfg.read_text().splitlines()
    
    if passwd:
        if copyid:
            typer.echo(f"Copying public key to [{hostname}] for {conn_name}")
            copy_pubkey_to_remote(hostname,user,port,retries=3)
            host_cfg = host_cfg + "  #Keyed yes\n"
    
    if keypair:
        typer.echo(f"Adding ssh connection {conn_name} to {address_string} with private-key {keypair}")

    ssh_cfg_content.append(host_cfg)
    ssh_cfg.write_text("\n".join(ssh_cfg_content)+"\n")
    typer.echo(f"Connection {conn_name} added")


def copy_pubkey_to_remote(hostname:str, user:str, port:str, retries: int):

    with open(f"{ssh_dir}/id_ed25519.pub") as f:
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
            typer.echo("Creating ssh dir failed on remote host")
            typer.echo(f"Remote STDOUT: {check_create_ssh_dir.stdout.strip()}\n\nremote STDERR: {check_create_ssh_dir.stderr.strip()} ")


        check_authorized_keys = conn.run("test -f $HOME/.ssh/authorized_keys", warn=True)
        if check_authorized_keys.return_code != 0:
            create_authorized_keys = conn.run("touch $HOME/.ssh/authorized_keys && chmod 600 $HOME/.ssh/authorized_keys")

            if create_authorized_keys.return_code != 0:
                typer.echo("Creating authorized_keys file failed")
                typer.echo(f"Remote STDOUT: {create_authorized_keys.stdout.strip()}\n\nremote STDERR: {create_authorized_keys.stderr.strip()} ")

        check_pub_key = conn.run("cat $HOME/.ssh/authorized_keys" , warn=True, hide=True)
        if pubkey.strip() not in check_pub_key.stdout.strip():
            insert_pub_key = conn.run(f"echo '{pubkey}' >> $HOME/.ssh/authorized_keys", warn=True) 
            if insert_pub_key.return_code != 0:
                typer.echo("Inserting pubkey failed")
                typer.echo(f"Remote STDOUT: {insert_pub_key.stdout.strip()}\n\nremote STDERR: {insert_pub_key.stderr.strip()} ")
            else:
                typer.echo("Public key copied")
        else:
            typer.echo("Pubkey already copied into remote authorized_keys")

    except Exception as e:
        typer.secho(f"Error: {type(e).__name__} – {e}", fg=typer.colors.BRIGHT_RED)

        if retries > 0:
            typer.echo(f"Retrying host [{hostname}] {retries} retries left...")
            copy_pubkey_to_remote(hostname,user,port,retries - 1)
        else:
            typer.echo(f"host [{hostname}] failed after multiple retries")
            sys.exit()


def list():

    host_block_list = []
    host_block = {}
    FIELDS = ["Host", "HostName", "User", "IdentityFile", "Port", "Keyed"]

    with ssh_cfg.open() as f:
        for line in f:
            stripped = line.strip()
            if not stripped: #or stripped.startswith('#'):
                continue
            
            key_value = stripped.split(maxsplit=1)
            if len(key_value) != 2:
                continue

            key , value = key_value
            key = key.strip()
            value = value.strip()

            if key == "Host":
                if value == "*":
                    continue
                if host_block:
                    host_block_list.append(host_block)
                host_block = {"Host": value}

            else:
                if key == "#Keyed":
                    key = key.strip("#")
                if key in FIELDS:
                    host_block[key] = value
        if host_block:
            host_block_list.append(host_block)
        
        table = Table(title="SSH Connections")

        for field in FIELDS:
            table.add_column(field)

        for host_block in host_block_list:
            row = [host_block.get(field, "-") for field in FIELDS]
            table.add_row(*row)
        
        console = Console()
        console.print(table)


def remove(conn_name: str, all: bool, remote: bool):

    ssh_cfg_content = ssh_cfg.read_text().splitlines()

    if all:
        confirmation: str = ""
        while confirmation not in ("y","n"):
            confirmation = input("deleting all sshu managed ssh configurations confirm y/N: ").strip().lower() or "n"
        
        if confirmation == "n":
            typer.echo("Operation canceled")
            sys.exit()
        elif confirmation == "y":
            typer.echo("Removing sshu configurations")
            remove_all_conn_from_cfg(ssh_cfg_content)

    elif conn_name:
        if not conn_name_exists(conn_name, ssh_cfg_content):
            typer.secho(f"No ssh connection named {conn_name} exists...", fg=typer.colors.BRIGHT_RED)
            sys.exit()
        if remote:
            remove_pubkey_from_remote(conn_name, ssh_cfg_content, retries=3)

        remove_conn_from_cfg(conn_name,ssh_cfg_content)
        typer.echo(f"Deleted ssh connection {conn_name}")


def conn_name_exists(conn_name: str, ssh_cfg_content):
    
    conn_name_list = []

    for line in ssh_cfg_content:
        if line.startswith('Host '):
            host = line.split(' ')[1]
            conn_name_list.append(host)

    if conn_name in conn_name_list:
        return True
    else:
        return False


def remove_conn_from_cfg(conn_name: str, ssh_cfg_content  ):

    ssh_cfg_str = "\n".join(ssh_cfg_content)

    host_block_to_delete = []
    conn_name_index = ssh_cfg_content.index("Host " + conn_name)

    for line in ssh_cfg_content[conn_name_index::]:
        if line.startswith('Host') and conn_name not in line:
            break
        else:
            host_block_to_delete.append(line)

    host_block_to_delete_str = "\n".join(host_block_to_delete)
    ssh_cfg_str = ssh_cfg_str.replace(host_block_to_delete_str,"")
    ssh_cfg.write_text(ssh_cfg_str)


def remove_all_conn_from_cfg(ssh_cfg_content):

    ssh_cfg_str = "\n".join(ssh_cfg_content)

    if sshu_marker not in ssh_cfg_content:
        typer.secho("No sshu configurations found to delete", fg=typer.colors.BRIGHT_RED)
        sys.exit()

    sshu_marker_index = ssh_cfg_content.index(sshu_marker)
    sshu_cfg_content = ssh_cfg_content[sshu_marker_index::]
    sshu_cfg_str = "\n".join(sshu_cfg_content)
    ssh_cfg_str = ssh_cfg_str.replace(sshu_cfg_str, "")
    ssh_cfg.write_text(ssh_cfg_str)


def remove_pubkey_from_remote(conn_name:str, ssh_cfg_content, retries):
    
    keyed_line = "#Keyed yes"

    host_block_to_delete = []
    conn_name_index = ssh_cfg_content.index("Host " + conn_name)

    for line in ssh_cfg_content[conn_name_index::]:
        if line.startswith('Host') and conn_name not in line:
            break
        if not line.strip():
            continue
        else:
            host_block_to_delete.append(line.strip())

    if keyed_line not in host_block_to_delete:
        typer.secho("This connection is not keyed, there is no public key to delete on the remote host...", fg=typer.colors.BRIGHT_RED)
        typer.echo("Please remove the --remote flag to delete the selected connection...")
        sys.exit()
    else:
        host_info = {} 

        for line in host_block_to_delete:
            key, value = line.split()
            host_info[key] = value

        with open(f"{ssh_dir}/id_ed25519.pub") as f:
            pubkey = f.read()
        
        
        conn = Connection(
            host=host_info["HostName"],
            user=host_info["User"],
            port=host_info["Port"]
        )

        try:
            get_authorized_keys = conn.run(f"cat $HOME/.ssh/authorized_keys", hide=True , warn=True)

            if get_authorized_keys.return_code != 0:
                typer.secho("Getting the authorized_keys file on remote host failed...", fg=typer.colors.BRIGHT_RED)
                typer.secho(f"ERROR - {get_authorized_keys.stderr.strip()}", fg=typer.colors.BRIGHT_RED)
                sys.exit()

            remote_authorized_keys = get_authorized_keys.stdout
            remote_authorized_keys = remote_authorized_keys.replace(pubkey,"").strip()
            update_authorized_keys = conn.run(f"echo '{remote_authorized_keys}' > $HOME/.ssh/authorized_keys", hide=True, warn=True)

            if update_authorized_keys.return_code != 0:
                typer.secho("Removing the pubkey from the remote host failed, aborting the remove action...", fg=typer.colors.BRIGHT_RED)
                typer.secho(f"ERROR - {update_authorized_keys.stderr.strip()}", fg=typer.colors.BRIGHT_RED)
                sys.exit()
            typer.echo(f"Public key successfully deleted from {host_info["HostName"]}")

        except Exception as e:
            typer.secho(f"Error: {type(e).__name__} – {e}", fg=typer.colors.BRIGHT_RED)
            
            if retries > 0:
                confirmation: str = ""
                while confirmation not in ("y","n"):
                    confirmation = input("Retry? Y/n: ").strip().lower() or "y"
                if confirmation == "n":
                    sys.exit()
                elif confirmation == "y":
                    typer.echo(f"Retrying pubkey removal from [{host_info["HostName"]}] {retries} retries left... ")
                    remove_pubkey_from_remote(conn_name, ssh_cfg_content, retries -1)
            else:
                typer.echo(f"host [{host_info["HostName"]}] failed after multiple retries")
                sys.exit()
