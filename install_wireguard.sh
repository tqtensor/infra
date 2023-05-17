#!/bin/bash

echo "Please paste your WireGuard configuration below:"
read -r CONFIG

sudo apt update
sudo apt -y install wireguard
echo "$CONFIG" | sudo tee /etc/wireguard/wg0.conf >/dev/null
sudo apt install resolvconf
sudo wg-quick up wg0
