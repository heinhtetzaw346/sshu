import typer
from pathlib import Path
from rich.table import Table
from rich.console import Console
import sys
import logging
from .config_utils import add_conn_to_cfg, parse_cfg_for_list, conn_name_exists, remove_conn_from_cfg, remove_all_conn_from_cfg, add_key_to_keys_dir
from .remote_utils import copy_pubkey_to_remote, remove_pubkey_from_remote

home_dir = Path.home()
ssh_dir = home_dir / ".ssh"
ssh_cfg = ssh_dir / "config"
sshu_marker = "#### Managed by SSHU ####"
keys_dir = ssh_dir / "keys"

logger = logging.getLogger(__name__)

def add(address_string: str, conn_name: str, passwd: bool, copyid: bool, keypair: str, port: str):
    logger.debug(f"Target connection name -> {conn_name}")

    if conn_name_exists(conn_name, ssh_cfg):
        logger.warning(f"Addition aborted: Connection '{conn_name}' already exists.")
        typer.secho(f"Connection {conn_name} already exists", fg=typer.colors.BRIGHT_RED)
        sys.exit()

    user,hostname = address_string.split('@')
    logger.debug(f"Parsed hostname -> {hostname}, user -> {user}")
    host_cfg = f"Host {conn_name}\n  HostName {hostname}\n  User {user}\n  Port {port}\n"
    
    if passwd:
        if copyid:
            typer.echo(f"Copying public key to [{hostname}] for {conn_name}")
            copy_pubkey_to_remote(hostname,user,port,retries=3)
            host_cfg = host_cfg + "  #Keyed yes\n"
    
    if keypair:
        keypair_to_add = Path(keypair)
        if not keypair_to_add.exists():
            logger.error(f"Failed to add connection: No key exists at -> {keypair}")
            typer.secho(f"No key exists at {keypair}", fg=typer.colors.BRIGHT_RED)
            sys.exit()
        else:
            new_key_file = add_key_to_keys_dir(keypair_to_add,keys_dir)
            logger.debug(f"IdentityFile -> {new_key_file}")
            host_cfg = host_cfg + f"  IdentityFile {new_key_file}\n  #Keyed yes"
    logger.debug(f"Generated host config block -> {host_cfg}")
    add_conn_to_cfg(host_cfg,ssh_cfg)
    logger.info(f"Successfully added connection '{conn_name}'.")
    typer.echo(f"Connection {conn_name} added")


def list():
    logger.debug("Parsing config to list connections.")

    FIELDS = ["Host", "HostName", "User", "Port", "Keyed", "IdentityFile"]
    
    host_block_list = parse_cfg_for_list(ssh_cfg,FIELDS)
        
    table = Table(title="SSH Connections")

    for field in FIELDS:
        table.add_column(field)

    for host_block in host_block_list:
        row = [host_block.get(field, "-") for field in FIELDS]
        table.add_row(*row)
    
    console = Console()
    console.print(table)


def remove(conn_name: str, all: bool, remote: bool):
    logger.debug(f"Removal target -> {conn_name if conn_name else 'ALL'}")

    if all:
        confirmation: str = ""
        while confirmation not in ("y","n"):
            confirmation = input("deleting all sshu managed ssh configurations confirm y/N: ").strip().lower() or "n"
        
        if confirmation == "n":
            logger.info("Removal operation canceled by user.")
            typer.echo("Operation canceled")
            sys.exit()
        elif confirmation == "y":
            typer.echo("Removing sshu configurations")
            remove_all_conn_from_cfg(ssh_cfg)
            logger.info("Removed all managed connections from config.")

    elif conn_name:
        if not conn_name_exists(conn_name, ssh_cfg):
            logger.warning(f"Deletion aborted: No ssh connection named '{conn_name}' exists.")
            typer.secho(f"No ssh connection named {conn_name} exists...", fg=typer.colors.BRIGHT_RED)
            sys.exit()
        if remote:
            logger.debug(f"Removing public key from remote -> {conn_name}")
            remove_pubkey_from_remote(conn_name, ssh_cfg, retries=3)

        remove_conn_from_cfg(conn_name,ssh_cfg)
        logger.info(f"Successfully removed connection '{conn_name}'.")
        typer.echo(f"Deleted ssh connection {conn_name}")
