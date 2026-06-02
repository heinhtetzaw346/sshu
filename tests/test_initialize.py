from sshu.cli import initialize_ssh_config, initialize_sshu_config
from pathlib import Path
import yaml

def test_init_sshu_config(temp: tuple):
    ssh_dir: Path = temp[1]
    sshu_cfg_file: Path = temp[2]

    sshu_cfg_file.write_text("""""")
    
    ret = initialize_sshu_config(ssh_dir, ssh_dir, sshu_cfg_file)
    
    assert ret == 0
    assert sshu_cfg_file.exists()

    with open(sshu_cfg_file,'r') as cfg_file:
        cfg_data = yaml.safe_load(cfg_file)

    default_config: dict = {
        "default_identity_key": "id_ed25519",
        "keys_dir": str(ssh_dir / "keys"),
        "key_scan": False
    }

    for key in default_config.keys():
        assert default_config[key] == cfg_data[key]


def test_init_ssh_config_keys(temp: tuple):
    ssh_dir: Path = temp[1]
    sshu_cfg_file: Path = temp[2]
    ret = initialize_ssh_config(ssh_dir, sshu_cfg_file)
    ssh_cfg: Path = ssh_dir / "config"
    keys_dir: Path = ssh_dir / "keys"
   
    assert ret == 0
    assert ssh_cfg.exists()
    assert keys_dir.exists()
    assert "#### Managed by SSHU ####" in ssh_cfg.read_text()

