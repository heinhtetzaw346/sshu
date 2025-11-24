from typer.testing import CliRunner
from importlib.metadata import version, PackageNotFoundError

from sshu.cli import app
from pathlib import Path

runner = CliRunner()

def test_cli_version():
    result = runner.invoke(app,["--version"])
    project_file: Path = Path.cwd() / "pyproject.toml"
    project_file_contents = project_file.read_text().splitlines()
    version_from_file = "0.0.0"
    for line in project_file_contents:
        if "version" in line:
            version_from_file = line.split(" = ")[1].replace('"','').strip()
            break
    try:
        __version__ = version("sshu")
    except PackageNotFoundError:
        __version__ = version_from_file
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__
