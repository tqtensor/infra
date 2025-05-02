import pulumi
import pulumi_gcp as gcp

from resources.utils import get_options
from resources.vm.keypair import pixelml_gcp_eu_west_4_key_pair

OPTS = get_options(
    profile="pixelml", region="us-east-1", type="resource", provider="gcp"
)


boot_image = gcp.compute.get_image(
    family="common-cu123", project="deeplearning-platform-release"
)

vss_ip = gcp.compute.Address(
    "vss_ip",
    name="vss-external-ip",
    address_type="EXTERNAL",
    region="europe-west4",
    opts=OPTS,
)

vss_instance = gcp.compute.Instance(
    "vss_instance",
    name="vss-instance",
    machine_type="a2-highgpu-4g",
    zone="europe-west4-a",
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
                    "nat_ip": vss_ip.address,
                    "network_tier": "PREMIUM",
                }
            ],
        )
    ],
    scheduling=gcp.compute.InstanceSchedulingArgs(
        on_host_maintenance="TERMINATE", automatic_restart=True
    ),
    metadata={
        "install-nvidia-driver": "true",
        "ssh-keys": pixelml_gcp_eu_west_4_key_pair.metadata["ssh-keys"],
    },
    tags=["http-server", "https-server"],
    opts=OPTS,
)

pulumi.export("VM: vss: IP", vss_ip.address)
