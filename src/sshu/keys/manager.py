import typer

app = typer.Typer()

@app.command("add")
def add_key():
    print("add key")

@app.command("rm")
def delete_key():
    print("delete key")

@app.command("ls")
def list_keys():
    print("list key")
