# SSH Utility

python cli app made with typer that manages ssh connections interactively with commands. Saves time from manually editing the ssh config file and easily connect to remote host with simple names.

## Commands

- ls -> list connections
- add -> add connections
- rm -> remove connections
- keys -> manage keys

## Supported OS

In current beta version v0.1.0, only Linux is supported. I will try to make it work on all major OS types.


## Releases

You can find all official releases on the [Releases page](../../releases).

The [`dist/`](./dist) directory contains the latest development build/binary.

## How to use

### Use the installation script.

Run the following command

```
curl -fsSL https://raw.githubusercontent.com/FuReAsu/sshu/refs/heads/main/install/linux_bash/sshu-installer.sh | sudo bash
```
Currently, this script is only usable for Debian-like distros, RedHat-like distros and SUSE distros and using bash-like shell.



### Install it yourself

Download the tar file from the releases.

Extract it

```
tar -xzvf sshu-beta-v0.1.1.tar.gz
```

Move it to a local binary directory.

```
sudo mv sshu /usr/local/bin/
```
You can now start running sshu commands.

## Command Reference

Currently only the main sshu cli app is working, keys haven't been worked on.
Even in the main sshu cli app, --keypair is not implemented yet.

All working commands:

- sshu ls
- sshu add --passwd user@hostname connection_name
- sshu add --passwd --copyid user@hostname connection_name
- sshu rm connection_name
- sshu rm --all


## What is used

Below are what I used in sshu:

- Typer for cli app
- Fabric for remote command execution over ssh connection

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
pyinstaller --name sshu --distpath ./dist -p ./sshu --onefile ./sshu/cli.py 
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
docker run --rm -it -v ./dist/linux_glibc:/dist local/sshu-build:latest
```

The resulting binary will be in the ./dist directory in the dir you specified.
