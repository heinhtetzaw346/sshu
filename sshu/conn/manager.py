import typer
import getpass
from pathlib import Path
from rich.table import Table
from rich.console import Console
from fabric import Connection

home_dir = Path.home()
ssh_dir = home_dir / ".ssh"
ssh_cfg = ssh_dir / "config"
sshu_marker = "#### Managed by SSHU ####"

def add(address_string: str, conn_name: str, passwd: bool, copyid: bool, keypair: str, port: str):

    if conn_name_exists(conn_name):
        typer.echo(f"Connection {conn_name} already exists")
        exit()

    user,hostname = address_string.split('@')
    host_cfg = f"Host {conn_name}\n  HostName {hostname}\n  User {user}\n  Port {port}\n"
    ssh_cfg_content = ssh_cfg.read_text().splitlines()
    
    if passwd:

        if copyid:
            typer.echo(f"Copying public key to server {address_string} for connection {conn_name}")

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

            check_pub_key_exists = conn.run(f"cat $HOME/.ssh/authorized_keys | grep '{pubkey}'", warn=True, hide=True)
            if check_pub_key_exists.return_code != 0:
                insert_pub_key = conn.run(f"echo '{pubkey}' >> $HOME/.ssh/authorized_keys", warn=True) 
                if insert_pub_key.return_code != 0:
                    typer.echo("Inserting pubkey failed")
                    typer.echo(f"Remote STDOUT: {insert_pub_key.stdout.strip()}\n\nremote STDERR: {insert_pub_key.stderr.strip()} ")
                else:
                    typer.echo("Public key copied")
            else:
                typer.echo("Pubkey already copied into remote authorized_keys")

            host_cfg = host_cfg + "  #Keyed yes\n"

    if keypair:
        typer.echo(f"Adding ssh connection {conn_name} to {address_string} with private-key {keypair}")

    ssh_cfg_content.append(host_cfg)
    ssh_cfg.write_text("\n".join(ssh_cfg_content)+"\n")
    typer.echo(f"Connection {conn_name} added")

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

def remove(conn_name: str, all: bool):

    ssh_cfg_content = ssh_cfg.read_text().splitlines()
    ssh_cfg_str = "\n".join(ssh_cfg_content)

    if all:
        confirmation: str = ""
        while confirmation not in ("y","n"):
            confirmation = input("deleting all sshu managed ssh configurations confirm y/N: ").strip().lower() or "n"
        
        if confirmation == "n":
            typer.echo("Operation canceled")
            exit()
        elif confirmation == "y":
            typer.echo("Removing sshu configurations")
            if sshu_marker not in ssh_cfg_content:
                typer.echo("No sshu configurations found to delete")
                exit()
            sshu_marker_index = ssh_cfg_content.index(sshu_marker)
            sshu_cfg_content = ssh_cfg_content[sshu_marker_index::]
            sshu_cfg_str = "\n".join(sshu_cfg_content)
            ssh_cfg_str = ssh_cfg_str.replace(sshu_cfg_str, "")
            ssh_cfg.write_text(ssh_cfg_str)

    elif conn_name:
        host_block_to_delete = []
        if not conn_name_exists(conn_name):
            typer.echo("No ssh connection named {conn_name} exists...")
            exit()
        else:
            conn_name_index = ssh_cfg_content.index("Host " + conn_name)
            for line in ssh_cfg_content[conn_name_index::]:
                if line.startswith('Host') and conn_name not in line:
                    break
                else:
                    host_block_to_delete.append(line)
            host_block_to_delete_str = "\n".join(host_block_to_delete)
            ssh_cfg_str = ssh_cfg_str.replace(host_block_to_delete_str,"")
            ssh_cfg.write_text(ssh_cfg_str)
            typer.echo(f"Deleted ssh connection {conn_name}")

def conn_name_exists(conn_name: str):
    ssh_cfg_content = ssh_cfg.read_text().splitlines()
    conn_name_list = []
    for line in ssh_cfg_content:
        if line.startswith('Host '):
            host = line.split(' ')[1]
            conn_name_list.append(host)

    if conn_name in conn_name_list:
        return True
    else:
        return False
