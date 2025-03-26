import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_us_central_1
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml",
    region="eu-west-4",
    type="resource",
    provider="gcp",
    protect=False,
)


pixelml_us_central_1_registry = gcp.artifactregistry.Repository(
    "pixelml_us_central_1_registry",
    format="DOCKER",
    repository_id="pixelml-us-central-1-registry",
    project=gcp_pixelml_us_central_1.project,
    location=gcp_pixelml_us_central_1.region,
    opts=OPTS,
)

pixelml_us_central_1_registry_public_access = gcp.artifactregistry.RepositoryIamMember(
    "pixelml_us_central_1_registry_public_access",
    project=gcp_pixelml_us_central_1.project,
    location=gcp_pixelml_us_central_1.region,
    repository=pixelml_us_central_1_registry.repository_id,
    role="roles/artifactregistry.reader",
    member="allUsers",
    opts=OPTS,
)
