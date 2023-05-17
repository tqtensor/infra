# Terraform on Proxmox

## Credentials for Proxmox integration
Create file `infra/credentials.auto.tfvars`

```txt
proxmox_api_url = "https://proxmox-server.com:8006/api2/json"
proxmox_api_token_id = "root@pam!terraform"
proxmox_api_token_secret = ""
```

## Prepare Ubuntu Cloud Init Image (with GPU)
https://austinsnerdythings.com/2021/08/30/how-to-create-a-proxmox-ubuntu-cloud-init-image/

```bash
export distro=focal # Ubuntu Server 20.04 LTS
wget "https://cloud-images.ubuntu.com/${distro}/current/${distro}-server-cloudimg-amd64.img"

apt update -y && apt install libguestfs-tools -y
virt-customize -a ${distro}-server-cloudimg-amd64.img --update
virt-customize -a ${distro}-server-cloudimg-amd64.img --install qemu-guest-agent,wget,curl,telnet,unzip

qm create 9000 --name "ubuntu-${distro}-q35-template" --memory 2048 --cores 2 --net0 virtio,bridge=vmbr1
qm importdisk 9000 ${distro}-server-cloudimg-amd64.img local-lvm
qm set 9000 --machine q35
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0
qm set 9000 --boot c --bootdisk scsi0
qm set 9000 --ide2 local-lvm:cloudinit
qm set 9000 --serial0 socket --vga serial0
qm set 9000 --hostpci0 0000:02:00,pcie=1,rombar=1
qm set 9000 --agent enabled=1

qm template 9000
```

## Prepare Ubuntu Cloud Init Image
https://austinsnerdythings.com/2021/08/30/how-to-create-a-proxmox-ubuntu-cloud-init-image/

```bash
export distro=focal # Ubuntu Server 20.04 LTS
wget "https://cloud-images.ubuntu.com/${distro}/current/${distro}-server-cloudimg-amd64.img"

apt update -y && apt install libguestfs-tools -y
virt-customize -a ${distro}-server-cloudimg-amd64.img --update
virt-customize -a ${distro}-server-cloudimg-amd64.img --install qemu-guest-agent,wget,curl,telnet,unzip

qm create 9001 --name "ubuntu-${distro}-template" --memory 2048 --cores 2 --net0 virtio,bridge=vmbr1
qm importdisk 9001 ${distro}-server-cloudimg-amd64.img local-lvm
qm set 9001 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9001-disk-0
qm set 9001 --boot c --bootdisk scsi0
qm set 9001 --ide2 local-lvm:cloudinit
qm set 9001 --serial0 socket --vga serial0
qm set 9001 --agent enabled=1

qm template 9001
```

## Errors
1. bool is required -> https://github.com/Telmate/terraform-provider-proxmox/issues/681
