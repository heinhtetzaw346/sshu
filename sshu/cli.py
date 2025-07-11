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
def add():
    """
    add new ssh connections
    """
    print("use this to add ssh connections")
    connmanager.add()

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
