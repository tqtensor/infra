import pulumi_gcp as gcp

from resources.utils import get_options

OPTS = get_options(
    profile="pixelml",
    region="eu-west-4",
    type="resource",
    provider="gcp",
    protect=False,
)


default_firewall = gcp.compute.Firewall(
    "default_firewall",
    name="global-firewall",
    network="default",
    allows=[
        {
            "protocol": "tcp",
            "ports": ["22", "80", "443", "8080", "8443", "30000-39999"],
        },
    ],
    source_ranges=["0.0.0.0/0"],
    opts=OPTS,
)
