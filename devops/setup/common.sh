#!/usr/bin/env bash

sudo apt update

sudo apt install -y python3 python3-venv python3-pip libaugeas0

# https://docs.docker.com/engine/install/ubuntu/
for pkg in docker.io docker-doc docker-compose docker-compose-v2 \
    podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Add Docker's official GPG key:
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update

for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc;
    do sudo apt remove $pkg; 
done

sudo apt install -y docker-ce docker-ce-cli \
    containerd.io docker-buildx-plugin docker-compose-plugin

python3 -m venv /opt/py-infra
/opt/py-infra/bin/pip install -r requirements.txt

echo
echo "Virtualenv has been setup in /tmp/infra. Run this command"
echo "source /opt/py-infra/bin/activate" before running invoke commands.