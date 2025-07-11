import typer
import importlib.metadata
from conn import manager as connmanager
from keys import manager as keysmanager

app = typer.Typer(help = "Manage SSH connections and keys",add_completion=False)
app.add_typer(keysmanager.app, name="keys", help="Manage SSH keys")

try:
    __version__ = importlib.metadata.version("sshu")
except importlib.metadata.PackageNotFoundError:
    __version__ = "v0.1.0"

@app.command()
def ls():
    """
    show available ssh connections and their status
    """
    print("use this to list ssh connections")
    connmanager.list()

@app.command()
def add(
    address_string: str = typer.Argument(..., help="SSH address string to the remote server eg. user@server.com"),
    conn_name: str = typer.Argument(..., help="SSH connection name to save eg. server1"),
    passwd: bool = typer.Option(False, "--passwd", help="use password authentication"),
    copyid: bool = typer.Option(False, "--copyid", help="perform ssh-copy-id to the remote server"),
    keypair: str = typer.Option(None, "--keypair", help="use keypair authentication and provide a private key")
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

    connmanager.add(address_string,conn_name,passwd,copyid,keypair)

@app.command()
def rm():
    """
    remove ssh connections
    """
    print("use this to remove ssh connections")
    connmanager.remove()

@app.command()
def version():
    """
    show the current app version
    """
    print(__version__)

def main():
    app()

if __name__ == "__main__":
    main()
