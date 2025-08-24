#!/bin/bash

sshu_ver="v0.1.1"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_FAMILY=$ID_LIKE
else
    echo "Cannot detect OS: /etc/os-release missing"
    exit 1
fi

echo "Installing python3 and tar..."
if [[ "$OS_FAMILY" =~ (ubuntu|debian) ]]; then
    echo "Debian/Ubuntu detected"
    apt-get update -y
    apt-get install -y python3 tar
elif [[ "$OS_FAMILY" =~ (rhel|centos|fedora) ]]; then
    echo "RHEL/CentOS/Fedora detected"
    yum update -y
    yum install -y python3 tar
elif [[ "$OS_FAMILY" =~ (suse|opensuse) ]]; then
    echo "SUSE detected"
    zypper refresh
    zypper install -y python3 tar
else
    echo "Unsupported OS family: $OS_FAMILY"
    exit 1
fi

echo "Creating temp dir to store sshu release"
mkdir -p /tmp/sshu

echo "Getting the sshu release..."
curl -L "https://github.com/FuReAsu/sshu/releases/download/$sshu_ver/sshu-beta-$sshu_ver-linux.tar.gz" -o /tmp/sshu/sshu.tar.gz

echo "Extracting the contents..."
tar -xzvf /tmp/sshu/sshu.tar.gz -C /tmp/sshu/ > /dev/null

echo "Installing the binary to /usr/local/bin"
mv /tmp/sshu/sshu/sshu /usr/local/bin

result=$?

echo "Cleaning the temp dir"
rm -rf /tmp/sshu

if [[ $result -eq 0 ]]; then
    echo "sshu has been installed. Please run [sshu version] to verify..."
else
    echo "sshu installation failed"
fi

