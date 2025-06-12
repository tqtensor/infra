#!/bin/bash

# Prompt for Tailscale auth key
read -p "Enter your Tailscale auth key: " AUTHKEY

if [ -z "$AUTHKEY" ]; then
    echo "Error: Auth key cannot be empty"
    exit 1
fi

sudo apt-get update -qq
sudo apt-get install -y -qq curl

curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --authkey="$AUTHKEY" --advertise-exit-node

echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf

echo "Tailscale setup complete. Rebooting in 5 seconds..."
sleep 5
sudo reboot
