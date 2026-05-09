import pytest
from typer.testing import CliRunner
from sshu.cli import app
from pathlib import Path

runner = CliRunner()

def test_cli_add_command(temp: tuple, monkeypatch):
    ssh_cfg: Path = temp[0]
    
    from sshu.conn import manager
    monkeypatch.setattr(manager, "ssh_cfg", ssh_cfg)
    
    result = runner.invoke(app, ["add", "cli_test_server", "-u", "cliapp", "-a", "192.168.99.99", "--passwd"])
    
    assert result.exit_code == 0
    assert "Connection cli_test_server added" in result.output
    
    cfg_content = ssh_cfg.read_text()
    assert "Host cli_test_server" in cfg_content
    assert "User cliapp" in cfg_content
    assert "HostName 192.168.99.99" in cfg_content

def test_cli_add_mutually_exclusive_auth(temp: tuple):
    # Testing that --passwd and --keypair fail when used together
    result = runner.invoke(app, ["add", "fail_server", "-u", "admin", "-a", "1.1.1.1", "--passwd", "--keypair", "dummy.pem"])
    assert result.exit_code == 1
    assert "You can't use both --passwd and --keypair" in result.output

def test_cli_add_missing_auth(temp: tuple):
    # Testing that missing both auth options fails
    result = runner.invoke(app, ["add", "fail_server", "-u", "admin", "-a", "1.1.1.1"])
    assert result.exit_code == 1
    assert "Please choose at least one authenticaiton option" in result.output