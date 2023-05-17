# Fix Proxmox GPU Passthrough

SSH into the Proxmox node and then run the following commands.
```bash
# create snippets folder
mkdir /var/lib/vz/snippets

# create script with content above from gpu-hookscript.sh
nano /var/lib/vz/snippets/gpu-hookscript.sh

# make it executable
chmod +x /var/lib/vz/snippets/gpu-hookscript.sh

# apply script to VM
qm set vmid --hookscript local:snippets/gpu-hookscript.sh
```
