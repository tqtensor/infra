import pulumi
import pulumi_gcp as gcp

from resources.utils import get_options
from resources.vm.keypair import pixelml_gcp_us_east_1_key_pair

OPTS = get_options(
    profile="pixelml", region="us-east-1", type="resource", provider="gcp"
)


boot_image = gcp.compute.get_image(
    family="common-cu123", project="deeplearning-platform-release"
)

workstation_gpu_ip = gcp.compute.Address(
    "workstation_gpu_ip",
    name="workstation-gpu-external-ip",
    address_type="EXTERNAL",
    region="us-east1",
    opts=OPTS,
)

workstation_gpu_instance = gcp.compute.Instance(
    "workstation_gpu_instance",
    name="workstation-gpu-instance",
    machine_type="g2-standard-12",
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
                    "nat_ip": workstation_gpu_ip.address,
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
        "ssh-keys": pixelml_gcp_us_east_1_key_pair.metadata["ssh-keys"],
    },
    opts=OPTS,
)

pulumi.export("VM: workstation_gpu: IP", workstation_gpu_ip.address)
