#!/usr/bin/env bash

sudo apt update

sudo apt install -y python3 python3-venv python3-pip libaugeas0
sudo python3 -m venv /opt/certbot/
sudo /opt/certbot/bin/pip install --upgrade pip
sudo /opt/certbot/bin/pip install certbot certbot-apache
sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot

sudo apt install -y docker


