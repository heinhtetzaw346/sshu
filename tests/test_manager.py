import pytest
from pathlib import Path
from sshu.conn.manager import add

def test_manager_add(temp: tuple, capsys, monkeypatch):
    ssh_cfg: Path = temp[0]
    
    from sshu.conn import manager
    monkeypatch.setattr(manager, "ssh_cfg", ssh_cfg)
    
    manager.add(
        conn_name="new_test_server",
        user="sysadmin",
        address="10.0.0.1",
        passwd=False,
        copyid=False,
        keypair="",
        port="2222"
    )
    
    cfg_content = ssh_cfg.read_text()
    assert "Host new_test_server" in cfg_content
    assert "HostName 10.0.0.1" in cfg_content
    assert "User sysadmin" in cfg_content
    assert "Port 2222" in cfg_content

def test_manager_add_duplicate(temp: tuple, capsys, monkeypatch):
    ssh_cfg: Path = temp[0]
    
    from sshu.conn import manager
    monkeypatch.setattr(manager, "ssh_cfg", ssh_cfg)
    
    with pytest.raises(SystemExit) as exc:
        manager.add(
            conn_name="unittest", # This is already in temp config
            user="sysadmin",
            address="10.0.0.1",
            passwd=False,
            copyid=False,
            keypair="",
            port="2222"
        )
    assert exc.value.code == None # sys.exit() without arguments defaults to None

