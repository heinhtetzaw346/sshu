# SSH Utility

python cli app made with typer that manages ssh connections interactively with commands. Saves time from manually editing the ssh config file and easily connect to remote host with simple names.

## Commands

- ls -> list connections
- add -> add connections
- rm -> remove connections

## Supported OS

Only linux with glibc libraries is tested by me. All the following OS will have binaries built for them.</br> 
sshu is not OS specific if installed with pip.
- Linux (glibc) Debian, RedHat
- Linux (musl) Alpine
- MacOS
- Windows

## Releases

You can find all official releases on the [Releases page](../../releases).

### Test Pypi
For dev pip packages, you can visit [https://test.pypi.org/project/sshu/](https://test.pypi.org/project/sshu/) and download from there.

## How to use

### Use the installation script.

> [!NOTE] 
> This hasn't been developed and tested fully yet.
</br>

Run the following command
```
curl -fsSL https://raw.githubusercontent.com/FuReAsu/sshu/refs/heads/main/install/linux_bash/sshu-installer.sh | sudo bash
```
Currently, this script is only usable for Debian-like distros, RedHat-like distros and SUSE distros and using bash-like shell.


### Install it yourself

Download the tar file from the releases. Or the binaries in github-actions workflows.

Extract it if tar or zip

```
tar -xzvf sshu-beta-v0.1.1.tar.gz
```

Move the binary to a local binary directory.

```
sudo mv sshu /usr/local/bin/
```
You can now start running sshu commands.

## Command Reference

Currently only the main sshu cli app is working, keys haven't been worked on.

All working commands:

- sshu ls
- sshu add connection_name -u user -a hostname --passwd
- sshu add connection_name -u user -a hostname --passwd --copyid
- sshu add connection_name -u user -a hostname --keypair /path/to/key
- sshu rm connection_name
- sshu rm --remote connection_name
- sshu rm --all

## Configuration File

The sshu configuration file exists at this path `$HOME/.config/sshu/config.yaml`
</br>
Example configs are as below:
```yaml
default_identity_key: id_ed25519
keys_dir: /home/fureasu/.ssh/keys
keys_scan: true
```
|Key|Description|Default|
|---|---|---|
|default_identity_key|The private key used for --copyid|id_ed25519|
|keys_dir|Where the store the imported private keys|<your_home_dir>/.ssh/keys|
|keys_scan|Whether to populare the known_hosts file when adding connections|true|

## What is used

Below are what I used in sshu:

- Python 3.12
- Typer for cli app
- Fabric for remote command execution over ssh connection

## Logging

SSHU logs background activity and debugging information to help you trace actions and troubleshoot errors. The log file is located at the app user data directory, typically `~/.local/share/sshu/sshu.log` on Linux.

## Build it yourself

Building it yourself is quick and easy, only taking upwards of 3 minutes. The best part is it is guaranteed to work.

Clone the repo 
``````
git clone https://github.com/FuReAsu/sshu.git && cd sshu
``````
<br/>

**Natively on your system**

Install dependencies

```
pip install -r requirement.txt
```

Run pyinstaller

```
pyinstaller --name sshu --distpath ./bin -p ./sshu --onefile ./sshu/cli.py
```

The resulting binary will be in the ./dist directory.
<br/>
<br/>

**With Docker**

There are different dockerfiles for different build configurations in the [build](build) directory.

Use glibc dockerfile for mainstream distros using glibc like most Debian-like and RedHat-like. Use musl dockerfile for distros that use musl like Alpine.

You can edit the Dockerfile to fit your needs if you want but. It's ready to run.

```
docker build -t local/sshu-build:latest -f build/Dockerfile.linux_glibc .
```

Run container to build image. Specifiy the correct ./dist sub dir.

```
docker run --rm -it -v ./bin/linux_glibc:/dist local/sshu-build:latest
```

The resulting binary will be in the ./bin directory.

You can then move this binary into the binary path. Like
```bash
cp bin/linux_glibc/sshu /usr/local/bin
```
