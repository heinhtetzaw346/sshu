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
    
    temp_cfg.write_text("""
#### Managed by SSHU ####

Host unittest
HostName unit
User test
Port 2375
#Keyed yes
IdentityFile /home/test/.ssh/keys/unittest.pem

Host pytest
HostName py
User test
Port 22
#Keyed no
        """)

    yield temp_cfg, temp_dir

    if temp_dir.exists():
        shutil.rmtree(temp_dir)
 
