import pulumi_gcp as gcp

from resources.utils import get_options

COUNTRY_CODES = {
    "aus": {"region": "aus-southeast-1", "zone": "australia-southeast1-c"},
    "bra": {"region": "sa-east-1", "zone": "southamerica-east1-c"},
    "can": {"region": "na-northeast-2", "zone": "northamerica-northeast2-c"},
    "deu": {"region": "eu-west-3", "zone": "europe-west3-c"},
    "nld": {"region": "eu-west-4", "zone": "europe-west4-c"},
    "qat": {"region": "me-central-1", "zone": "me-central1-c"},
    "sgp": {"region": "asia-southeast-1", "zone": "asia-southeast1-c"},
    "twn": {"region": "asia-east-1", "zone": "asia-east1-c"},
    "usa": {"region": "us-east-1", "zone": "us-east1-c"},
}


def create_tailscale_instance(
    country_code: str,
) -> gcp.compute.Instance:
    boot_image = gcp.compute.get_image(family="debian-12", project="debian-cloud")

    region = COUNTRY_CODES[country_code]["region"]
    zone = COUNTRY_CODES[country_code]["zone"]
    opts = get_options(
        profile="pixelml",
        region=region,
        type="resource",
        provider="gcp",
        kwargs={"ignore_changes": ["bootDisk"]},
    )

    external_ip = gcp.compute.Address(
        f"ts-{country_code}-external-ip",
        name=f"ts-{country_code}-external-ip",
        address_type="EXTERNAL",
        region="-".join(zone.split("-")[:-1]),
        opts=opts,
    )

    instance = gcp.compute.Instance(
        f"ts-{country_code}-instance",
        name=f"ts-{country_code}-instance",
        machine_type="e2-small",
        zone=zone,
        boot_disk=gcp.compute.InstanceBootDiskArgs(
            initialize_params=gcp.compute.InstanceBootDiskInitializeParamsArgs(
                image=boot_image.self_link,
                size=10,
            )
        ),
        network_interfaces=[
            gcp.compute.InstanceNetworkInterfaceArgs(
                network="default",
                access_configs=[
                    {
                        "nat_ip": external_ip.address,
                        "network_tier": "PREMIUM",
                    }
                ],
            )
        ],
        allow_stopping_for_update=True,
        scheduling=gcp.compute.InstanceSchedulingArgs(automatic_restart=True),
        opts=opts,
    )
    return instance


aus_instance = create_tailscale_instance(country_code="aus")
bra_instance = create_tailscale_instance(country_code="bra")
can_instance = create_tailscale_instance(country_code="can")
deu_instance = create_tailscale_instance(country_code="deu")
nld_instance = create_tailscale_instance(country_code="nld")
sgp_instance = create_tailscale_instance(country_code="sgp")
twn_instance = create_tailscale_instance(country_code="twn")
qat_instance = create_tailscale_instance(country_code="qat")
usa_instance = create_tailscale_instance(country_code="usa")
