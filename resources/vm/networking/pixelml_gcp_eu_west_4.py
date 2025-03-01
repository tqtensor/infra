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
