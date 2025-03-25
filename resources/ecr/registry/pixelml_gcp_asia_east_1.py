import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_asia_east_1
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="asia-east-1", type="resource", provider="gcp"
)


pixelml_asia_east_1_registry = gcp.artifactregistry.Repository(
    "pixelml_asia_east_1_registry",
    format="DOCKER",
    repository_id="pixelml-asia-east-1-registry",
    project=gcp_pixelml_asia_east_1.project,
    location=gcp_pixelml_asia_east_1.region,
    opts=OPTS,
)
