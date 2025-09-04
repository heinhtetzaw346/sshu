import typer
from pathlib import Path
from rich.table import Table
from rich.console import Console
import sys
from .config_utils import conn_name_exists, remove_conn_from_cfg, remove_all_conn_from_cfg
from .remote_utils import copy_pubkey_to_remote, remove_pubkey_from_remote

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


def list():

    host_block_list = []
    host_block = {}
    FIELDS = ["Host", "HostName", "User", "Port", "Keyed", "IdentityFile"]

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
