# NextCloud All-In-One (AIO) Setup Guide

## Prerequisites
- A Linux system with root/sudo access
- Internet connection
- Open ports: 80, 8080, and 8443

## Step 1: Install Docker
Run these commands to install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world
```

## Step 2: Start NextCloud AIO Container
Run this command to start the NextCloud AIO container:
```bash
docker run -d \
--sig-proxy=false \
--name nextcloud-aio-mastercontainer \
--restart always \
--publish 80:80 \
--publish 8080:8080 \
--publish 8443:8443 \
--volume nextcloud_aio_mastercontainer:/mnt/docker-aio-config \
--volume /var/run/docker.sock:/var/run/docker.sock:ro \
nextcloud/all-in-one:20230530_084406-latest
```

## Step 3: Access NextCloud
Open your web browser and go to `https://<your-server-ip>:8080/setup` to access the NextCloud web interface. Follow the on-screen instructions to complete the setup process.
```bash
pulumi stack output | grep Nextcloud
```

## Step 4: Retrieve Admin Password
```bash
sudo docker exec nextcloud-aio-mastercontainer grep password /mnt/docker-aio-config/data/configuration.json
```

Happy NextClouding! 🚀
