import typer
from pathlib import Path
from rich.table import Table
from rich.console import Console


home_dir = Path.home()
ssh_dir = home_dir / ".ssh"
ssh_cfg = ssh_dir / "config"

def add(address_string: str, conn_name: str, passwd: bool, copyid: bool, keypair: str):
    if passwd:
        user_and_hostname = address_string.split('@')
        user = user_and_hostname[0]
        hostname = user_and_hostname[1]
        
        host_cfg = f"Host {conn_name}\n  HostName {hostname}\n  User {user}\n"
        ssh_cfg_string = ssh_cfg.read_text()
        ssh_cfg_content = ssh_cfg.read_text().splitlines()

        if copyid:
            typer.echo(f"copying public key to server {address_string} for connection {conn_name}")
            host_cfg = host_cfg + "  #Keyed yes\n"
        else:
            host_cfg = host_cfg + "  #Keyed no\n"

        if conn_name not in ssh_cfg_string:
            ssh_cfg_content.append(host_cfg)
            ssh_cfg.write_text("\n".join(ssh_cfg_content)+"\n")
            typer.echo(f"Connection {conn_name} added")
        else:
            typer.echo(f"Connection {conn_name} already exists")

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

def remove():
    typer.echo("remove connection")
