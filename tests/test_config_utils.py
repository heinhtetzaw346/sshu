from sshu.conn.config_utils import add_conn_to_cfg, conn_name_exists, parse_cfg_for_list, add_key_to_keys_dir, remove_all_conn_from_cfg, remove_conn_from_cfg
from pathlib import Path
import pytest

def test_add_new_conn(temp: tuple):
    ssh_cfg: Path = temp[0] 
    host_cfg = f"Host hello\n  HostName world\n  User helloworld\n  Port 8200\n  #Keyed yes"
    add_conn_to_cfg(host_cfg, ssh_cfg)

    ssh_cfg_content = ssh_cfg.read_text()
    assert host_cfg in ssh_cfg_content


def test_conn_name_exists_pos(temp: tuple):
    ssh_cfg: Path = temp[0]
    result = conn_name_exists("unittest",ssh_cfg)
    assert result


def test_conn_name_exists_neg(temp: tuple):
    ssh_cfg: Path = temp[0]
    result = conn_name_exists("gibberish",ssh_cfg)
    assert not result


def test_parse_cfg_for_list(temp: tuple):
    ssh_cfg: Path = temp[0]
    FIELDS = ["Host", "HostName", "User", "Port", "Keyed", "IdentityFile"]
    host_block_list = parse_cfg_for_list(ssh_cfg,FIELDS)
    assert host_block_list == [
        {
            "Host": "unittest",
            "HostName": "unit",
            "User": "test",
            "Port": "2375",
            "Keyed": "yes",
            "IdentityFile": "unittest.pem"
        },
        {
            "Host": "pytest",
            "HostName": "py",
            "User": "test",
            "Port": "22",
            "Keyed": "no"
        }
    ]


def test_remove_all_conn_from_cfg(temp: tuple):
    ssh_cfg: Path = temp[0]
    remove_all_conn_from_cfg(ssh_cfg)
    ssh_cfg_content = ssh_cfg.read_text().strip()
    assert ssh_cfg_content == ""


def test_remove_conn_from_cfg(temp: tuple):
    ssh_cfg: Path = temp[0]
    remove_conn_from_cfg("unittest",ssh_cfg)
    ssh_cfg_content = ssh_cfg.read_text()
    existing_conn = """
Host unittest
HostName unit
User test
Port 2375
#Keyed yes
IdentityFile /home/test/.ssh/keys/unittest.pem
    """
    assert not existing_conn in ssh_cfg_content


def test_add_key_to_keys_dir(temp: tuple):
    ssh_dir: Path = temp[1]
    keys_dir = ssh_dir / "keys"
    if not keys_dir.exists():
        keys_dir.mkdir(mode=0o700)
    keypair_to_add = ssh_dir / "unittestkey.pem"
    if not keypair_to_add.exists():
        keypair_to_add.touch(mode=0o600)
    privkey = """
-----BEGIN OPENSSH PRIVATE KEY-----
unittestkeydwap[di9aufpeosjflajwiauwpoakdwd
jeoiafjoeafkwopakdwoa;fjiv9pip[ri4wyoiufioa
djapoupoefpoaifoapfkoefkopefopeidajdajdddd
-----END OPENSSH PRIVATE KEY-----
"""
    keypair_to_add.write_text(privkey)
    add_key_to_keys_dir(keypair_to_add,keys_dir)

    new_keypair = keys_dir / "unittestkey.pem"
    assert new_keypair.exists() and new_keypair.read_text() == privkey

def test_remove_conn_no_glob_match(temp: tuple):
    ssh_cfg: Path = temp[0]
    
    # Add a host with a similar name
    ssh_cfg.write_text(ssh_cfg.read_text() + "\nHost unittest-dev\n  HostName py\n  User test\n  Port 22\n")
    
    # Remove unittest
    remove_conn_from_cfg("unittest", ssh_cfg)
    
    ssh_cfg_content = ssh_cfg.read_text()
    
    # unittest should be gone
    assert "Host unittest\n" not in ssh_cfg_content
    # unittest-dev should STILL be there
    assert "Host unittest-dev\n" in ssh_cfg_content

def test_remove_conn_above_marker_aborts(temp: tuple):
    ssh_cfg: Path = temp[0]
    
    # Re-write config to put a host ABOVE the marker
    ssh_cfg.write_text("Host unmanaged\n  HostName unmanaged.test\n\n" + ssh_cfg.read_text())
    
    # Removing 'unmanaged' should trigger a SystemExit(1)
    with pytest.raises(SystemExit) as exc_info:
        remove_conn_from_cfg("unmanaged", ssh_cfg)
        
    assert exc_info.value.code == 1
    
    # Verify it was NOT deleted
    ssh_cfg_content = ssh_cfg.read_text()
    assert "Host unmanaged\n" in ssh_cfg_content
