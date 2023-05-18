resource "proxmox_vm_qemu" "teleport" {
  name        = "teleport"
  desc        = "Ubuntu Server"
  vmid        = 202
  target_node = "hpz440"

  agent = 1

  clone   = "ubuntu-jammy-template"
  cores   = 2
  sockets = 1
  cpu     = "host"
  memory  = 2048
  balloon = 1024

  network {
    bridge   = "vmbr0"
    model    = "virtio"
    firewall = true
    macaddr  = "02:01:01:01:01:74"
  }

  disk {
    storage = "local-lvm"
    type    = "virtio"
    size    = "30G"
  }

  os_type    = "cloud-init"
  ipconfig0  = "ip=11.11.1.74/16,gw=11.11.1.1"
  nameserver = "1.1.1.1"
  ciuser     = "terrabot"
  sshkeys    = <<EOF
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC1s3xm/TxBJ38g2jMlg1MseGEy7gYQ7++ofccdwgkuYkVMx/6+li4bimhlCcxfoWea1nqowoM8R/OkkJI2SSVjHEoIm1i9cfZ+VADzoDGuHvGpqud/TQqsskiryQv8hx8upKbvAHRYt8c1YJTEKrWYJd6UW9xIg/+IwyqzlScHeNeomxKFPy3j7GBeAzzh3R+tVVWLajNqUIuHBxmlUkHU4Ko6B/YQziI1PLQXesvLK3/ab/XRlkWh6ZIrK6/xYF+rs/MGUZD43nZrpBUFH4u0ht7uUCrdcVxUoaHZcnKk5qF3nvDzzL2K9SqyY6NfOUjnpXxDSNFh5unzwkNfqTr/3mDoDeXonxrd3QaEKjgZzqkyZ4YwNGGfFxGhFsUwyLa6MJ3KGE98hTmMGtYnAuGqvBQf1BVKhcVzXjK8R37nEayNXZT163felTWgNnSnspRNMnpx5epIIvlCODIundCMTLF8zneIsRUk5NLebmpKbSS+799BtH4UMZax2kW2yzk= terrabot
    EOF

  connection {
    type        = "ssh"
    user        = self.ciuser
    private_key = file("~/.ssh/terrabot")
    host        = "11.11.1.74"
  }

  provisioner "file" {
    source      = "install_docker.sh"
    destination = "/tmp/install_docker.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo chmod +x /tmp/install_docker.sh",
      "/tmp/install_docker.sh",
    ]
  }

  provisioner "file" {
    source      = "install_conda.sh"
    destination = "/tmp/install_conda.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo chmod +x /tmp/install_conda.sh",
      "/tmp/install_conda.sh",
    ]
  }

  lifecycle {
    ignore_changes = [
      qemu_os,
      disk[0].type,
      disk[0].size
    ]
  }
}
