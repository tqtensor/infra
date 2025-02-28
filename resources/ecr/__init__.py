import pulumi
import pulumi_gcp as gcp
from pulumi import Output

from resources.providers import gcp_pixelml_asia_east_1
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="asia-east-1", type="resource", provider="gcp"
)


pixelml_asia_east_1_ecr = gcp.artifactregistry.Repository(
    "pixelml_asia_east_1_ecr",
    repository_id="pixeml-asia-east1-registry",
    format="DOCKER",
    opts=OPTS,
)

pulumi.export(
    "ECR: asia-east-1",
    Output.all(
        pixelml_asia_east_1_ecr.location,
        gcp_pixelml_asia_east_1.project,
        pixelml_asia_east_1_ecr.name,
    ).apply(lambda args: args[0] + "-docker.pkg.dev/" + args[1] + "/" + args[2]),
)
