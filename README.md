# SSH Utility

python cli app made with typer that manages ssh connections interactively with commands. Saves time from manually editing the ssh config file and easily connect to remote host with simple names.

## Commands

- ls -> list connections
- add -> add connections
- rm -> remove connections
- keys -> manage keys

## Supported OS

In current beta version v0.1.0, only Linux is supported. I will try to make it work on all major OS types.


## How to use

Download the tar file from the releases.

Extract it

```
tar -xzvf sshu-beta-v0.1.0.tar.gz
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

You can edit the Dockerfile to fit your needs if you want but. It's ready to run.

```
docker build -t local/sshu-build:latest .
```

Run container to build image

```
docker run --rm -it -v ./dist:/dist local/sshu-build:latest
```

The resulting binary will be in the ./dist directory.
