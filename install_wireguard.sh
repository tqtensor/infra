#!/bin/bash

echo "Please paste your WireGuard configuration below:"
read -r CONFIG

sudo DEBIAN_FRONTEND=noninteractive apt update
sudo DEBIAN_FRONTEND=noninteractive apt -y -qq install wireguard
echo "$CONFIG" | sudo tee /etc/wireguard/wg0.conf >/dev/null
sudo DEBIAN_FRONTEND=noninteractive apt install resolvconf
sudo wg-quick up wg0
