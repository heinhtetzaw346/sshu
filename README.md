# SSH Utility

python cli app made with typer that

## Commands

- ls -> list connections
- add -> add connections
- rm -> remove connections
- keys -> manage keys

## Supported OS

In current beta version v0.1.0, only Linux is supported. I will try to make it work on all major OS types.


## How to use

Download the binary from the releases.

Move it to a local binary directory.

```
sudo mv sshu /usr/local/sshu
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

    
