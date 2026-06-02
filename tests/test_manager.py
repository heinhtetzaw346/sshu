import pytest
from pathlib import Path
from sshu.conn.manager import add

def test_manager_add(temp: tuple, capsys, monkeypatch):
    ssh_cfg: Path = temp[0]
    temp_dir = temp[1]
    sshu_cfg_file = temp[2]
    
    from sshu.conn import manager
    monkeypatch.setattr(manager, "ssh_cfg", ssh_cfg)
    from sshu.conn import config_utils
    monkeypatch.setattr(config_utils, "sshu_cfg_dir", temp_dir)
    monkeypatch.setattr(config_utils, "sshu_cfg_file", sshu_cfg_file)
    
    manager.add(
        conn_name="new_test_server",
        user="sysadmin",
        address="10.0.0.1",
        passwd=False,
        copyid=False,
        keypair="",
        port="2222",
        key_scan=False
    )
    
    cfg_content = ssh_cfg.read_text()
    assert "Host new_test_server" in cfg_content
    assert "HostName 10.0.0.1" in cfg_content
    assert "User sysadmin" in cfg_content
    assert "Port 2222" in cfg_content

def test_manager_add_duplicate(temp: tuple, capsys, monkeypatch):
    ssh_cfg: Path = temp[0]
    temp_dir = temp[1]
    sshu_cfg_file = temp[2]
    
    from sshu.conn import manager
    monkeypatch.setattr(manager, "ssh_cfg", ssh_cfg)
    from sshu.conn import config_utils
    monkeypatch.setattr(config_utils, "sshu_cfg_dir", temp_dir)
    monkeypatch.setattr(config_utils, "sshu_cfg_file", sshu_cfg_file)
    
    with pytest.raises(SystemExit) as exc:
        manager.add(
            conn_name="unittest", # This is already in temp config
            user="sysadmin",
            address="10.0.0.1",
            passwd=False,
            copyid=False,
            keypair="",
            port="2222",
            key_scan=False
        )
    assert exc.value.code == 1

