import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_asia_east_1
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml",
    region="asia-east-1",
    type="resource",
    provider="gcp",
)


nginx_ip_asia_east_1 = gcp.compute.Address(
    "nginx_ip_asia_east_1",
    name="nginx-controller-ip",
    network_tier="PREMIUM",
    project=gcp_pixelml_asia_east_1.project,
    region=gcp_pixelml_asia_east_1.region,
    opts=OPTS,
)
