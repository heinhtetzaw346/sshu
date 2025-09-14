from typer.testing import CliRunner
from importlib.metadata import version, PackageNotFoundError

from sshu.cli import app

runner = CliRunner()

def test_cli_version():
    result = runner.invoke(app,["version"])
    try:
        __version__ = version("sshu")
    except PackageNotFoundError:
        __version__ = "0.0.0"
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__
