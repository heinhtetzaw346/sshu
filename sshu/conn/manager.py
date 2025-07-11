

def add(address_string: str, conn_name: str, passwd: bool, copyid: bool, keypair: str):
    if passwd:
        print(f"adding ssh connection {conn_name} to {address_string} with passwd method")
        if copyid:
            print(f"copying public key to server {address_string} for connection {conn_name}")
    if keypair:
        print(f"adding ssh connection {conn_name} to {address_string} with private-key {keypair}")

def list():
    print("list connection")

def remove():
    print("remove connection")
