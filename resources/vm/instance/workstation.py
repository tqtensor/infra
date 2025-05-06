import pulumi
import pulumi_gcp as gcp

from resources.utils import get_options
from resources.vm.keypair import pixelml_gcp_us_east_1_key_pair

OPTS = get_options(
    profile="pixelml", region="us-east-1", type="resource", provider="gcp"
)


boot_image = gcp.compute.get_image(family="debian-11", project="debian-cloud")

workstation_ip = gcp.compute.Address(
    "workstation_ip",
    name="workstation-external-ip",
    address_type="EXTERNAL",
    region="us-east1",
    opts=OPTS,
)

workstation_instance = gcp.compute.Instance(
    "workstation_instance",
    name="workstation-instance",
    machine_type="e2-standard-4",
    zone="us-east1-c",
    boot_disk=gcp.compute.InstanceBootDiskArgs(
        initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
            image=boot_image.self_link,
            size=400,
        )
    ),
    network_interfaces=[
        gcp.compute.InstanceNetworkInterfaceArgs(
            network="default",
            access_configs=[
                {
                    "nat_ip": workstation_ip.address,
                    "network_tier": "PREMIUM",
                }
            ],
        )
    ],
    scheduling=gcp.compute.InstanceSchedulingArgs(automatic_restart=True),
    metadata={
        "ssh-keys": pixelml_gcp_us_east_1_key_pair.metadata["ssh-keys"],
    },
    opts=OPTS,
)

pulumi.export("VM: workstation: IP", workstation_ip.address)
