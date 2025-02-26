import pulumi_gcp as gcp

from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="europe-west-4", type="resource", provider="gcp"
)


auto_pilot_eu_west_4_cluster = gcp.container.Cluster(
    "auto_pilot_eu_west_4_cluster",
    name="auto-pilot-europe-west-4-cluster",
    location="europe-west4",
    enable_autopilot=True,
    opts=OPTS,
)
