import typer
import importlib.metadata
import os
import subprocess
from pathlib import Path
from sshu.conn import manager as connmanager
from sshu.keys import manager as keysmanager

app = typer.Typer(help = "Manage SSH connections and keys",add_completion=False)
app.add_typer(keysmanager.app, name="keys", help="Manage SSH keys")

try:
    __version__ = importlib.metadata.version("sshu")
except importlib.metadata.PackageNotFoundError:
    __version__ = "v0.1.0"

home_dir = Path.home()
ssh_dir = home_dir / ".ssh"
ssh_cfg = ssh_dir / "config"
ssh_cfg_bk = ssh_dir / "config.og.bk"
sshu_marker = "#### Managed by SSHU ####"

def main():
    initialize_ssh_config()
    app()

def initialize_ssh_config():
    if not ssh_dir.exists():
        ssh_dir.mkdir(mode=0o700)
        typer.echo("Created ssh directory because it doesn't exist yet")
    if not ssh_cfg.exists():
        ssh_cfg.touch(mode=0o600)
        typer.echo("Created ssh/config file because it doesn't exist yet")
    elif not ssh_cfg_bk.exists():
        typer.echo("Backing up the ssh config file before editing it")
        ssh_cfg_bk.write_text(ssh_cfg.read_text())
    
    ssh_cfg_contents = ssh_cfg.read_text().splitlines()

    if sshu_marker not in ssh_cfg_contents:
        ssh_cfg_contents.append("\n")
        ssh_cfg_contents.append(sshu_marker)
        ssh_cfg.write_text("\n".join(ssh_cfg_contents) + "\n")

def initialize_ssh_keys():
   ssh_dir_contents = os.listdir(ssh_dir)
   if not "id_ed25519.pub" in ssh_dir_contents:
       print("Creating an ed25519 key because it doesn't exist yet")
       process = subprocess.Popen(
           ["ssh-keygen", "-t", "ed25519"],
           stdin=subprocess.PIPE,
           stdout=subprocess.PIPE,
           stderr=subprocess.PIPE,
           text=True
       ) 
       output = process.communicate(input="\n\n\n")
       print(output[0])

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
    initialize_ssh_keys()

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
def rm():
    """
    remove ssh connections
    """
    typer.echo("use this to remove ssh connections")
    connmanager.remove()

@app.command()
def version():
    """
    show the current app version
    """
    typer.echo(__version__)

if __name__ == "__main__":
    main()
