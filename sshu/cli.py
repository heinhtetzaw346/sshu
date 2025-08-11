import typer
import importlib.metadata
import os
import logging
import appdirs
import subprocess
from pathlib import Path
from sshu.conn import manager as connmanager
from sshu.keys import manager as keysmanager

app = typer.Typer(help = "Manage SSH connections and keys",add_completion=False)
app.add_typer(keysmanager.app, name="keys", help="Manage SSH keys")

try:
    __version__ = importlib.metadata.version("sshu")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.1"

home_dir = Path.home()
ssh_dir = home_dir / ".ssh"
ssh_cfg = ssh_dir / "config"
sshu_marker = "#### Managed by SSHU ####"

@app.callback()
def main(verbose: int = typer.Option(0, "-v", count=True)):
    if verbose == 0:
        stdout_level = logging.CRITICAL
    elif verbose == 1:
        stdout_level = logging.INFO
    else:
        stdout_level = logging.DEBUG
    
    configure_logging(stdout_level)
    initialize_ssh_config()
    initialize_ssh_keys()

def configure_logging(stdout_level=logging.CRITICAL):

    log_dir = appdirs.user_data_dir("sshu", "FuReAsu")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "sshu.log")
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_format)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(stdout_level)
    stdout_format = logging.Formatter("%(levelname)s: %(message)s")
    stdout_handler.setFormatter(stdout_format)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    return logger

def initialize_ssh_config():
    
    logging.info(f"Initializing ssh directory and its contents at {ssh_dir}...")

    if not ssh_dir.exists():
        ssh_dir.mkdir(mode=0o700)
        logging.debug(f"Created {ssh_dir} with permission 700")

    if not ssh_cfg.exists():
        ssh_cfg.touch(mode=0o600)
        logging.debug(f"Created {ssh_cfg} with permission 600")
    
    ssh_cfg_contents = ssh_cfg.read_text().splitlines()

    if sshu_marker not in ssh_cfg_contents:
        ssh_cfg_contents.append("\n")
        ssh_cfg_contents.append(sshu_marker)
        ssh_cfg.write_text("\n".join(ssh_cfg_contents) + "\n")
        logging.debug(f"Added '{sshu_marker}' to {ssh_cfg}")

def initialize_ssh_keys():

   ssh_dir_contents = os.listdir(ssh_dir)
   if not "id_ed25519.pub" in ssh_dir_contents:
       process = subprocess.Popen(
           ["ssh-keygen", "-t", "ed25519", "-f", f"{home_dir}/.ssh/id_ed25519", "-N", ""],
           stdin=subprocess.PIPE,
           stdout=subprocess.PIPE,
           stderr=subprocess.PIPE,
           text=True
       ) 
       output = process.communicate(input="\n\n\n")
       logging.debug(f"pubkey generation output -> {output}")

@app.command()
def ls():
    """
    show available ssh connections and their status
    
    Host\t -> Name of the connection\n
    HostName\t -> Server address (IP or Hostname)\n
    User\t -> SSH User\n
    IdentityFile -> SSH Private Key\n
    Port\t -> SSH Port\n
    Keyed\t -> Whether ssh-copy-id is performed (only present on connections managed by sshu)\n

    """
    connmanager.list()

@app.command()
def add(
    address_string: str = typer.Argument(..., help="SSH address string to the remote server eg. user@server.com"),
    conn_name: str = typer.Argument(..., help="SSH connection name to save eg. server1"),
    passwd: bool = typer.Option(False, "--passwd", help="use password authentication"),
    copyid: bool = typer.Option(False, "--copyid", help="perform ssh-copy-id to the remote server"),
    keypair: str = typer.Option(None, "--keypair", help="use keypair authentication and provide a private key"),
    port: str = typer.Option(22, help="SSH connection port; default is 22")
):
    """
    add new ssh connections
    """

    if passwd and keypair:
        typer.echo("You can't use both --passwd and --keypair please use only one authentication option", err=True)
        raise typer.Exit(code=1)

    if not passwd and not keypair:
        typer.echo("Please choose at least one authenticaiton option --passwd or --keypair", err=True)
        raise typer.Exit(code=1)

    if keypair and copyid:
        typer.echo("--keypair and --copyid can't be used together",err=True)
        raise typer.Exit(code=1)

    connmanager.add(address_string,conn_name,passwd,copyid,keypair, port)

@app.command()
def rm(
    conn_name: str = typer.Argument(None,help="SSH connection name to remove"),
    all: bool = typer.Option(False,"--all", help="Remove all ssh connections. This will restore the ssh config file to the state before sshu was used"),
    remote: bool = typer.Option(False, "--remote", help="Remove the public key from the remote server. This can only be done for connections with Keyed=yes")
):
    """
    remove ssh connections
    """
    connmanager.remove(conn_name, all, remote)

@app.command()
def version():
    """
    show the current app version
    """
    typer.echo(__version__)

if __name__ == "__main__":
    app()
