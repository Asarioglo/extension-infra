#!/usr/bin/env bash

sudo apt update

sudo apt install libnss3-tools

(cd /tmp && curl -JLO https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-arm64)
chmod +x /tmp/mkcert-v*-linux-arm64
sudo cp /tmp/mkcert-v*-linux-arm64 /usr/local/bin/mkcert

mkcert --version

mkdir $HOME/certs && cd $HOME/certs

mkcert staging.host.my