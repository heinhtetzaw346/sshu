import typer
import importlib.metadata

app = typer.Typer()

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

@app.command()
def add():
    """
    add new ssh connections
    """
    print("use this to add ssh connections")

@app.command()
def rm():
    """
    remove ssh connections
    """
    print("use this to remove ssh connections")

@app.command()
def keys():
    """
    manage ssh keys
    """

@app.command()
def version():
    """
    show the current app version
    """
    print(__version__)

def main():
    app()

if __name__ == "__main__":
    app()
