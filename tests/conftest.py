import pytest
import shutil
from pathlib import Path

@pytest.fixture
def temp():
    temp_dir = Path.cwd() / ".temp"
    temp_cfg = temp_dir / "tmp_config"
    
    if not temp_dir.exists():
        temp_dir.mkdir(mode=0o700)
    if not temp_cfg.exists():
        temp_dir.touch(mode=0o600)
    
    yield temp_cfg, temp_dir

    if temp_dir.exists():
        shutil.rmtree(temp_dir)
 
