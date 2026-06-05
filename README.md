# SSHU (SSH Utility)

![Python Version](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-GPL_3.0%20license-yellow)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

**SSHU** is an interactive, command-line application designed to simplify SSH connection management. Built with Python and Typer, it eliminates the need to manually edit your `~/.ssh/config` file, allowing you to easily add, remove, list, and connect to remote hosts using simple, memorable names.

---

## Table of Contents

- [Features](#features)
- [Supported Platforms](#supported-platforms)
- [Installation](#installation)
  - [Using the Installer Scripts](#using-the-installer-scripts)
  - [Manual Installation](#manual-installation)
- [Usage / Command Reference](#usage--command-reference)
- [Configuration](#configuration)
- [Logging & Troubleshooting](#logging--troubleshooting)
- [Building from Source](#building-from-source)
- [Technologies Used](#technologies-used)

---

## Features

- **Interactive Management**: Add, remove, and list SSH connections from the command line.
- **Key Management**: Automatically copy identities or use specific key pairs.
- **Portability**: Available as a standalone binary or via pip.
- **Host Key Scanning**: Automatically populates `known_hosts` when adding new connections, either via CLI flags or configuration.
- **Autocompletion**: Built-in autocompletion for commands and connection names.

## Supported Platforms

SSHU is OS-agnostic when installed via pip. Standalone binaries are available for the following operating systems:

- **Linux (glibc)**: Debian, Ubuntu, RedHat, Fedora, etc.
- **Linux (musl)**: Alpine
- **macOS**
- **Windows**

*(Note: Currently, only Linux with glibc is fully tested natively, but binaries are built for all listed platforms.)*

---

## Installation

You can find all official releases on the [Releases page](../../releases). For developmental pip packages, visit [Test PyPI](https://test.pypi.org/project/sshu/).

### Using the Installer Scripts

You can install SSHU quickly using our automated installation scripts.

**Linux / macOS**
```bash
curl -fsSL https://raw.githubusercontent.com/heinhtetzaw346/sshu/refs/heads/main/install/sshu_installer.sh | sh
```
*Note: The script automatically detects if you are running as root and selects the appropriate installation path (`/usr/local/bin` for root, `~/.local/bin` for non-root).*

**Windows (PowerShell)**
```powershell
Invoke-RestMethod -Uri https://raw.githubusercontent.com/heinhtetzaw346/sshu/refs/heads/main/install/sshu_installer.ps1 | Invoke-Expression
```
*Note: Run PowerShell as Administrator for a system-wide installation, or as a normal user to install locally for your account.*

### Installing from PyPI

You can also install SSHU as a standard Python package. We recommend using a virtual environment (`venv`) to avoid system-wide package conflicts.

```bash
# Create a virtual environment
python3 -m venv sshu-env

# Activate the environment
# On Linux/macOS:
source sshu-env/bin/activate
# On Windows:
# .\sshu-env\Scripts\activate

# Install SSHU
pip install sshu
```
*(Alternatively, you can use `pipx install sshu` to install it globally in an isolated environment).*

### Manual Installation

1. Download the appropriate binary for your platform from the [Releases page](../../releases).
2. Make the downloaded binary executable (Linux/macOS):
   ```bash
   chmod +x sshu-linux-glibc
   ```
3. Move the binary to a directory included in your system's `PATH`:
   ```bash
   sudo mv sshu-linux-glibc /usr/local/bin/sshu
   ```
4. Verify the installation:
   ```bash
   sshu --help
   ```

---

## Usage / Command Reference

Manage your connections directly from the CLI. 

### Listing Connections
```bash
sshu ls
```

### Adding a Connection
```bash
# Basic setup with a password prompt
sshu add connection_name -u user -a hostname --passwd

# Add and immediately copy SSH ID to the remote host
sshu add connection_name -u user -a hostname --passwd --copyid

# Add using an existing, specific keypair
sshu add connection_name -u user -a hostname --keypair /path/to/key

# Add connection with a custom SSH port (e.g., 8282)
sshu add connection_name -u user -a hostname -k /path/to/key --port 8282

# Add connection and scan server host key to known_hosts
sshu add connection_name -u user -a hostname -P --key-scan
```

### Removing a Connection
```bash
# Remove a connection locally (supports autocompletion)
sshu rm connection_name

# Remove a connection locally and clean up remote keys
sshu rm --remote connection_name

# Remove all managed connections and restore SSH config
sshu rm --all
```

---

## Configuration

SSHU utilizes a YAML configuration file located at: `$HOME/.config/sshu/config.yaml`

### Example Configuration

```yaml
default_identity_key: id_ed25519
keys_dir: /home/fureasu/.ssh/keys
key_scan: false
```

### Configuration Reference

| Key | Description | Default Value |
|---|---|---|
| `default_identity_key` | The private key used when the `--copyid` flag is passed. | `id_ed25519` |
| `keys_dir` | Directory where imported private keys are stored. | `~/.ssh/keys` |
| `key_scan` | Whether to populate the `known_hosts` file automatically when adding connections. | `false` |

---

## Logging & Troubleshooting

SSHU logs background activity and debugging information to help you trace actions and troubleshoot errors. 

- **Linux**: `~/.local/share/sshu/sshu.log`
- **macOS/Windows**: Located in the respective user data directory for the application.

---

## Building from Source

Building SSHU yourself is fast (usually under 3 minutes) and ensures compatibility with your specific environment.

First, clone the repository:
```bash
git clone https://github.com/FuReAsu/sshu.git
cd sshu
```

### Method 1: Natively

1. Install Python dependencies:
   ```bash
   pip install -r requirement.txt
   ```
2. Build the executable using PyInstaller:
   ```bash
   pyinstaller --name sshu --distpath ./bin -p ./sshu --onefile ./sshu/cli.py
   ```
3. The resulting binary will be placed in the `./dist` (or `./bin` depending on your PyInstaller version) directory.

### Method 2: With Docker

Different Dockerfiles are available in the `build/` directory for various target environments (e.g., `glibc` for mainstream Linux, `musl` for Alpine).

1. Build the Docker image:
   ```bash
   docker build -t local/sshu-build:latest -f build/Dockerfile.linux_glibc .
   ```
2. Run the container to compile the binary and extract it to your local `./bin` directory:
   ```bash
   docker run --rm -it -v $(pwd)/bin/linux_glibc:/dist local/sshu-build:latest
   ```
3. Move the built binary to your path:
   ```bash
   sudo cp bin/linux_glibc/sshu /usr/local/bin
   ```

---

## Technologies Used

- **[Python 3.12](https://www.python.org/)**: Core programming language.
- **[Typer](https://typer.tiangolo.com/)**: For building the robust Command Line Interface.
- **[Fabric](https://www.fabfile.org/)**: For executing remote commands over SSH.
