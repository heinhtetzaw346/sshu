import typer
import getpass
from pathlib import Path
from rich.table import Table
from rich.console import Console
from fabric import Connection

home_dir = Path.home()
ssh_dir = home_dir / ".ssh"
ssh_cfg = ssh_dir / "config"
ssh_cfg_og_bk = ssh_dir / "config.og.bk"

def add(address_string: str, conn_name: str, passwd: bool, copyid: bool, keypair: str, port: str):
    if passwd:
        user,hostname = address_string.split('@')
        
        host_cfg = f"Host {conn_name}\n  HostName {hostname}\n  User {user}\n  Port {port}\n"
        ssh_cfg_string = ssh_cfg.read_text()
        ssh_cfg_content = ssh_cfg.read_text().splitlines()

        if conn_name not in ssh_cfg_string:
            ssh_cfg_content.append(host_cfg)
            ssh_cfg.write_text("\n".join(ssh_cfg_content)+"\n")
            typer.echo(f"Connection {conn_name} added")
        else:
            typer.echo(f"Connection {conn_name} already exists")

        if copyid:
            typer.echo(f"copying public key to server {address_string} for connection {conn_name}")

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
                typer.echo("creating ssh dir failed on remote host")
                typer.echo(f"remote STDOUT: {check_create_ssh_dir.stdout.strip()}\n\nremote STDERR: {check_create_ssh_dir.stderr.strip()} ")


            check_authorized_keys = conn.run("test -f $HOME/.ssh/authorized_keys", warn=True)
            if check_authorized_keys.return_code != 0:
                create_authorized_keys = conn.run("touch $HOME/.ssh/authorized_keys && chmod 600 $HOME/.ssh/authorized_keys")

                if create_authorized_keys.return_code != 0:
                    typer.echo("creating authorized_keys file failed")
                    typer.echo(f"remote STDOUT: {create_authorized_keys.stdout.strip()}\n\nremote STDERR: {create_authorized_keys.stderr.strip()} ")

            check_pub_key_exists = conn.run(f"cat $HOME/.ssh/authorized_keys | grep '{pubkey}'", warn=True)
            if check_pub_key_exists.return_code != 0:
                insert_pub_key = conn.run(f"echo '{pubkey}' >> $HOME/.ssh/authorized_keys", warn=True) 
                if insert_pub_key.return_code != 0:
                    typer.echo("inserting pubkey failed")
                    typer.echo(f"remote STDOUT: {insert_pub_key.stdout.strip()}\n\nremote STDERR: {insert_pub_key.stderr.strip()} ")
                else:
                    typer.echo("public key copied")
            else:
                typer.echo("pubkey already copied into remote authorized_keys")

            host_cfg = host_cfg + "  #Keyed yes\n"

    if keypair:
        typer.echo(f"adding ssh connection {conn_name} to {address_string} with private-key {keypair}")

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
    if all:
        default_ssh_config = ssh_cfg_og_bk
