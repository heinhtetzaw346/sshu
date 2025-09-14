from sshu.cli import initialize_ssh_config, initialize_ssh_keys
from pathlib import Path

def test_init_ssh_config_keys(temp: tuple):
    ssh_dir: Path = temp[1]
    initialize_ssh_config(ssh_dir)
    ssh_cfg: Path = ssh_dir / "config"
    keys_dir: Path = ssh_dir / "keys"
    
    assert ssh_cfg.exists()
    assert keys_dir.exists()
    assert "#### Managed by SSHU ####" in ssh_cfg.read_text()


def test_init_keys(temp: tuple):
    ssh_dir: Path = temp[1]
    initialize_ssh_keys(ssh_dir)
    pubkey = ssh_dir / "id_ed25519.pub"
    privkey = ssh_dir / "id_ed25519"
    
    assert pubkey.exists() and privkey.exists()
