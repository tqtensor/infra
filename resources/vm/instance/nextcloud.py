import pulumi
import pulumi_gcp as gcp

from resources.utils import get_options
from resources.vm.keypair import pixelml_gcp_eu_west_4_key_pair

OPTS = get_options(
    profile="pixelml", region="eu-west-4", type="resource", provider="gcp"
)


boot_image = gcp.compute.get_image(family="debian-11", project="debian-cloud")

nextcloud_ip = gcp.compute.Address(
    "nextcloud_ip",
    name="nextcloud-external-ip",
    address_type="EXTERNAL",
    region="europe-west4",
    opts=OPTS,
)

nextcloud_instance = gcp.compute.Instance(
    "nextcloud_instance",
    name="nextcloud-instance",
    machine_type="e2-standard-2",
    zone="europe-west4-c",
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
                    "nat_ip": nextcloud_ip.address,
                    "network_tier": "PREMIUM",
                }
            ],
        )
    ],
    allow_stopping_for_update=True,
    scheduling=gcp.compute.InstanceSchedulingArgs(automatic_restart=True),
    metadata={
        "ssh-keys": pixelml_gcp_eu_west_4_key_pair.metadata["ssh-keys"],
    },
    opts=OPTS,
)

pulumi.export("VM: NextCloud: IP", nextcloud_ip.address)
