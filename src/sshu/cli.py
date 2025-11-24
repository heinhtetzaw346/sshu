import typer
import importlib.metadata
import os
import sys
import logging
import appdirs
import yaml
from pathlib import Path
from sshu.conn import manager as connmanager
from sshu.keys import manager as keysmanager

help_message = """  Manage SSH connections and keys\n
                    Examples\n
                    sshu add --passwd --copyid sysadmin@192.168.1.25 db_server\n
                    sshu add --keypair ~/.ssh/Web_Server_Key.pem sysadmin@192.168.1.50 web_server\n
                    sshu ls\n
                    sshu rm web_server\n
                    sshu rm --remote db_server\n
                    \n
                    You can also use short forms of the options\n
                    sshu add -P -c sysadmin@192.168.1.25 db_server\n
                    sshu add -k ~/.ssh/Web_Server_Key.pem sysadmin@192.168.1.50 web_server\n
                    sshu rm -r db_server\n
                    \n
                    You can also specify ports for non default ssh ports by using --port or -p\n
                    sshu add --port 8282 --keypair ~/.ssh/Web_Server_Key.pem sysadmin@192.168.1.50 web_server
               """

app = typer.Typer(help = help_message,add_completion=False)
app.add_typer(keysmanager.app, name="keys", help="Manage SSH keys")

home_dir = Path.home()
ssh_dir = home_dir / ".ssh"
sshu_marker = "#### Managed by SSHU ####"
sshu_cfg_dir = Path(appdirs.user_config_dir("sshu", "FuReAsu"))
sshu_cfg_file = sshu_cfg_dir / "config.yaml"

def show_version():
    """
    show the current app version
    """
    try:
        __version__ = importlib.metadata.version("sshu")
    except importlib.metadata.PackageNotFoundError:
        __version__ = "0.1.3-beta"
    print(__version__)

@app.callback(invoke_without_command=True)
def main(
    verbose: int = typer.Option(0, "--verbose", "-v", count=True),
    version: bool = typer.Option(False, "--version", is_eager=True)
    ):
   
    if version:
        show_version()
        raise typer.Exit(code=0)
    if verbose == 0:
        stdout_level = logging.CRITICAL
    elif verbose == 1:
        stdout_level = logging.INFO
    else:
        stdout_level = logging.DEBUG
    
    configure_logging(stdout_level)
    initialize_sshu_config(ssh_dir,sshu_cfg_dir, sshu_cfg_file)
    initialize_ssh_config(ssh_dir, sshu_cfg_file)
    initialize_ssh_keys(ssh_dir, sshu_cfg_file)

def configure_logging(stdout_level=logging.CRITICAL):

    log_dir = appdirs.user_data_dir("sshu", "FuReAsu")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
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

def initialize_ssh_config(ssh_dir: Path, sshu_cfg_file: Path):
  
    with open(sshu_cfg_file,'r') as cfg_file:
        cfg_data: dict = yaml.safe_load(cfg_file) or {}

    keys_dir: Path = Path(cfg_data["keys_dir"])

    ssh_cfg = ssh_dir / "config"
    if not ssh_dir.exists():
        ssh_dir.mkdir(mode=0o700)
        logging.debug(f"Created {ssh_dir} with permission 700")

    if not keys_dir.exists():
        keys_dir.mkdir(mode=0o700)
        logging.debug(f"Created {keys_dir} with permission 700")

    if not ssh_cfg.exists():
        ssh_cfg.touch(mode=0o600)
        logging.debug(f"Created {ssh_cfg} with permission 600")
    
    ssh_cfg_contents = ssh_cfg.read_text().splitlines()

    if sshu_marker not in ssh_cfg_contents:
        ssh_cfg_contents.append("\n")
        ssh_cfg_contents.append(sshu_marker)
        ssh_cfg.write_text("\n".join(ssh_cfg_contents) + "\n")
        logging.debug(f"Added '{sshu_marker}' to {ssh_cfg}")

def initialize_ssh_keys(ssh_dir: Path, sshu_cfg_file: Path):

    with open(sshu_cfg_file,'r') as cfg_file:
        cfg_data: dict = yaml.safe_load(cfg_file) or {}

    default_identity_key: str = cfg_data["default_identity_key"]

    ssh_dir_contents = os.listdir(ssh_dir)
    logging.debug(f"ssh dir contents -> {ssh_dir_contents}")
    if not default_identity_key in ssh_dir_contents:
        typer.secho(f"No {default_identity_key} file found in {ssh_dir} directory. Please check the default_identity_key value in {str(sshu_cfg_file)}", fg=typer.colors.BRIGHT_RED)
        typer.secho("Or create the key by running ssh-keygen", fg=typer.colors.BRIGHT_RED)
        logging.info("The default identity key is not found in .ssh dir")
        sys.exit()
    else:
        logging.info("The default identity key already exists.")
   
def initialize_sshu_config(ssh_dir: Path, sshu_cfg_dir: Path, sshu_cfg_file: Path):

    if not os.path.exists(sshu_cfg_dir):
        os.makedirs(sshu_cfg_dir)
        logging.info(f"sshu config dir doesn't exit creating.")
        logging.debug(f"sshu config dir -> {sshu_cfg_dir}.")
    else:
        logging.info("sshu config dir already exists.")
    
    sshu_cfg_file = sshu_cfg_dir / "config.yaml" 
    if not sshu_cfg_file.exists():
        sshu_cfg_file.touch(mode=0o600)
        logging.info("Created sshu config file.")
        logging.debug(f"Created file -> {str(sshu_cfg_file)}")
    else:
        logging.info("sshu config file already exists.")

    default_config: dict = {
        "default_identity_key": "id_ed25519",
        "keys_dir": str(ssh_dir / "keys"),
        "keys_scan": True
    }

    with open(sshu_cfg_file,'r') as cfg_file:
        cfg_data: dict = yaml.safe_load(cfg_file) or {}

    new_cfg_data: dict = cfg_data

    if len(cfg_data) == 0:
        new_cfg_data = default_config
        logging.info("No config data exists yet, populating with default values")
    else:
        for key in default_config.keys():
            if not key in cfg_data.keys() or not cfg_data[key]:
                new_cfg_data[key]=default_config[key]
                logging.info(f"No key {key} set, setting it the default value.")
                logging.debug(f"Key -> {key}. Value -> {cfg_data[key]}")
            else:
                continue
    
    with open(sshu_cfg_file,'w') as cfg_file:
        yaml.safe_dump(new_cfg_data,cfg_file)

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
    passwd: bool = typer.Option(False, "--passwd", "-P", help="use password authentication"),
    copyid: bool = typer.Option(False, "--copyid", "-c", help="perform ssh-copy-id to the remote server"),
    keypair: str = typer.Option(None, "--keypair", "-k", help="use keypair authentication and provide a private key"),
    port: str = typer.Option(22, "--port", "-p", help="SSH connection port; default is 22")
):
    """
    add new ssh connections
    """

    if passwd and keypair:
        typer.secho("You can't use both --passwd and --keypair please use only one authentication option", fg=typer.colors.BRIGHT_RED, err=True)
        raise typer.Exit(code=1)

    if not passwd and not keypair:
        typer.secho("Please choose at least one authenticaiton option --passwd or --keypair", fg=typer.colors.BRIGHT_RED, err=True)
        raise typer.Exit(code=1)

    if keypair and copyid:
        typer.secho("--keypair and --copyid can't be used together", fg=typer.colors.BRIGHT_RED, err=True)
        raise typer.Exit(code=1)

    connmanager.add(address_string,conn_name,passwd,copyid,keypair, port)

@app.command()
def rm(
    conn_name: str = typer.Argument(None,help="SSH connection name to remove"),
    all: bool = typer.Option(False,"--all", "-A", help="Remove all ssh connections. This will restore the ssh config file to the state before sshu was used"),
    remote: bool = typer.Option(False, "--remote", "-r", help="Remove the public key from the remote server. This can only be done for connections with Keyed=yes")
):
    """
    remove ssh connections
    """
    if all and remote:
        typer.secho("You can't use --remote with --all option", fg=typer.colors.BRIGHT_RED, err=True)
        raise typer.Exit(code=1)
    connmanager.remove(conn_name, all, remote)

if __name__ == "__main__":
    app()
