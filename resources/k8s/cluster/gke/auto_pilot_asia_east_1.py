import pulumi_gcp as gcp

from resources.utils import get_options

OPTS = get_options(
    profile="pixelml",
    region="asia-east-1",
    type="resource",
    provider="gcp",
)


auto_pilot_asia_east_1_cluster = gcp.container.Cluster(
    "auto_pilot_asia_east_1_cluster",
    name="auto-pilot-asia-east-1-cluster",
    location="asia-east1",
    enable_autopilot=True,
    opts=OPTS,
)
