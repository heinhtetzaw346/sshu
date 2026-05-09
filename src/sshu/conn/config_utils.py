import typer
from pathlib import Path
import sys
import os

sshu_marker = "#### Managed by SSHU ####"

def parse_cfg_for_list(ssh_cfg: Path, FIELDS: list):
    host_block_list = []
    host_block = {}
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
                if key == "IdentityFile":
                    value = value.split("/")[-1]
                if key == "#Keyed":
                    key = key.strip("#")
                if key in FIELDS:
                    host_block[key] = value
        if host_block:
            host_block_list.append(host_block)

    return host_block_list


def add_conn_to_cfg(host_cfg: str, ssh_cfg: Path):

    ssh_cfg_content = ssh_cfg.read_text().splitlines()
    ssh_cfg_content.append(host_cfg)
    ssh_cfg.write_text("\n".join(ssh_cfg_content)+"\n")


def conn_name_exists(conn_name: str, ssh_cfg: Path):
    
    ssh_cfg_content = ssh_cfg.read_text().splitlines()
    conn_name_list = []

    for line in ssh_cfg_content:
        if line.startswith('Host '):
            host = line.split(' ')[1]
            conn_name_list.append(host)

    if conn_name in conn_name_list:
        return True
    else:
        return False


def remove_conn_from_cfg(conn_name: str, ssh_cfg: Path):

    ssh_cfg_content = ssh_cfg.read_text().splitlines()

    if sshu_marker not in ssh_cfg_content:
        typer.secho("There are no sshu managed connections yet", fg=typer.colors.BRIGHT_RED)
        sys.exit(1)

    marker_index = ssh_cfg_content.index(sshu_marker)
    before_marker = ssh_cfg_content[:marker_index + 1]
    managed_content = ssh_cfg_content[marker_index + 1:]

    try:
        conn_name_index = managed_content.index("Host " + conn_name)
    except ValueError:
        typer.secho(f"The connection {conn_name} is not managed by sshu", fg=typer.colors.BRIGHT_RED)
        sys.exit(1)

    host_end_index = conn_name_index + 1
    for line in managed_content[conn_name_index + 1:]:
        if line.startswith('Host '):
            break
        host_end_index += 1

    del managed_content[conn_name_index:host_end_index]
    
    new_content = before_marker + managed_content
    ssh_cfg.write_text("\n".join(new_content) + "\n")


def remove_all_conn_from_cfg(ssh_cfg: Path):

    ssh_cfg_content = ssh_cfg.read_text().splitlines()
    ssh_cfg_str = "\n".join(ssh_cfg_content)

    if sshu_marker not in ssh_cfg_content:
        typer.secho("No sshu configurations found to delete", fg=typer.colors.BRIGHT_RED)
        sys.exit()

    sshu_marker_index = ssh_cfg_content.index(sshu_marker)
    sshu_cfg_content = ssh_cfg_content[sshu_marker_index::]
    sshu_cfg_str = "\n".join(sshu_cfg_content)
    ssh_cfg_str = ssh_cfg_str.replace(sshu_cfg_str, "")
    ssh_cfg.write_text(ssh_cfg_str)

def add_key_to_keys_dir(keypair_to_add: Path, keys_dir: Path):

    keyfile = os.path.basename(keypair_to_add)
    key_file_content = keypair_to_add.read_text()
    new_key_file = keys_dir / keyfile
    
    if not new_key_file.exists():
        new_key_file.touch(mode=0o600)
        new_key_file.write_text(key_file_content)
        typer.echo(f"Copied {keyfile} to the keys directory")
    else:
        typer.echo(f"{keyfile} already exists in the keys directory")
    return new_key_file
