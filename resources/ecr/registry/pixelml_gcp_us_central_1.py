from typing import cast

import pulumi_gcp as gcp
from pulumi import Output

from resources.providers import gcp_pixelml_us_central_1
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml",
    region="eu-west-4",
    type="resource",
    provider="gcp",
)


pixelml_us_central_1_registry = gcp.artifactregistry.Repository(
    "pixelml_us_central_1_registry",
    format="DOCKER",
    repository_id="pixelml-us-central-1-registry",
    project=cast(Output[str], gcp_pixelml_us_central_1.project),
    location=cast(Output[str], gcp_pixelml_us_central_1.region),
    opts=OPTS,
)

pixelml_us_central_1_registry_public_access = gcp.artifactregistry.RepositoryIamMember(
    "pixelml_us_central_1_registry_public_access",
    project=cast(Output[str], gcp_pixelml_us_central_1.project),
    location=cast(Output[str], gcp_pixelml_us_central_1.region),
    repository=pixelml_us_central_1_registry.repository_id,
    role="roles/artifactregistry.reader",
    member="allUsers",
    opts=OPTS,
)
