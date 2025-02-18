#!/usr/bin/env bash

./common.sh

sudo apt install libnss3-tools

(cd /tmp && curl -JLO https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-arm64)
chmod +x /tmp/mkcert-v*-linux-arm64
sudo cp /tmp/mkcert-v*-linux-arm64 /usr/local/bin/mkcert
mkcert --version
mkcert -install


if ! grep -q "vm.my" /etc/hosts; then
    echo "127.0.0.0   vm.my" | sudo tee -a /etc/hosts
fi
