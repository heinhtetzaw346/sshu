import typer
import logging

logger = logging.getLogger(__name__)

app = typer.Typer()

@app.command("add")
def add_key():
    logger.debug("add_key command called")
    print("add key")

@app.command("rm")
def delete_key():
    logger.debug("delete_key command called")
    print("delete key")

@app.command("ls")
def list_keys():
    logger.debug("list_keys command called")
    print("list key")
