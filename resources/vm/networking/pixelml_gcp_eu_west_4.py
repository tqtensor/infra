import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_eu_west_4
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml",
    region="eu-west-4",
    type="resource",
    provider="gcp",
)


nginx_ip_eu_west_4 = gcp.compute.Address(
    "nginx_ip_eu_west_4",
    name="nginx-controller-ip",
    network_tier="PREMIUM",
    project=gcp_pixelml_eu_west_4.project,
    region=gcp_pixelml_eu_west_4.region,
    opts=OPTS,
)

default_firewall = gcp.compute.Firewall(
    "default_firewall",
    name="global-firewall",
    network="default",
    allows=[
        {
            "protocol": "tcp",
            "ports": ["22", "80", "443", "30000-39999"],
        },
    ],
    source_ranges=["0.0.0.0/0"],
    opts=OPTS,
)
