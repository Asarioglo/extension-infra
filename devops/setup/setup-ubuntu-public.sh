#!/usr/bin/env bash

./common.sh

sudo apt update

sudo python3 -m venv /opt/certbot/
sudo /opt/certbot/bin/pip install --upgrade pip
sudo /opt/certbot/bin/pip install certbot certbot-apache
sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot

