import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_us_central_1
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="us-central-1", type="resource", provider="gcp"
)


cloudrun_sa = gcp.serviceaccount.Account(
    "cloudrun_sa",
    account_id="cloudrun-sa-us-central-1",
    opts=OPTS,
)

roles = [
    "roles/run.serviceAgent",
]
for role in roles:
    gcp.projects.IAMMember(
        f"cloudrun_sa_{role}",
        project=gcp_pixelml_us_central_1.project,
        role=role,
        member=cloudrun_sa.email.apply(lambda email: f"serviceAccount:{email}"),
    )
