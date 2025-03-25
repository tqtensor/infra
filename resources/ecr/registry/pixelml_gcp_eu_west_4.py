import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_eu_west_4
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="eu-west-4", type="resource", provider="gcp"
)


pixelml_eu_west_4_registry = gcp.artifactregistry.Repository(
    "pixelml_eu_west_4_registry",
    format="DOCKER",
    repository_id="pixelml-eu-west-4-registry",
    project=gcp_pixelml_eu_west_4.project,
    location=gcp_pixelml_eu_west_4.region,
    opts=OPTS,
)

pixelml_eu_west_4_registry_public_access = gcp.artifactregistry.RepositoryIamMember(
    "pixelml_eu_west_4_registry_public_access",
    project=gcp_pixelml_eu_west_4.project,
    location=gcp_pixelml_eu_west_4.region,
    repository=pixelml_eu_west_4_registry.repository_id,
    role="roles/artifactregistry.reader",
    member="allUsers",
    opts=OPTS,
)
