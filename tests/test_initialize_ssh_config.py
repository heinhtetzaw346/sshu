from sshu.cli import initialize_ssh_config
from pathlib import Path
import pytest

def test_init_ssh_config(temp: tuple):
    ssh_dir: Path = temp[1]
    initialize_ssh_config(ssh_dir)
    ssh_cfg: Path = ssh_dir / "config"
    
    assert ssh_cfg.exists()

def test_init_keys_dir(temp: tuple):
    ssh_dir: Path = temp[1]
    initialize_ssh_config(ssh_dir)
    keys_dir: Path = ssh_dir / "keys"
    
    assert keys_dir.exists()

def test_init_ssh_config_marker(temp: tuple):
    ssh_dir: Path = temp[1]
    initialize_ssh_config(ssh_dir)
    ssh_cfg: Path = ssh_dir / "config"

    if ssh_cfg.exists():
        assert "#### Managed by SSHU ####" in ssh_cfg.read_text()
    else:
        pytest.fail("ssh config is not created!")
