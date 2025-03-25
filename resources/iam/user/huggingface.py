import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_asia_east_1
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="asia-east-1", type="resource", provider="gcp"
)


huggingface_sa = gcp.serviceaccount.Account(
    "huggingface_sa",
    account_id="huggingface-sa-europe-west-4",
    opts=OPTS,
)

roles = [
    "roles/artifactregistry.reader",
]
for role in roles:
    gcp.projects.IAMMember(
        f"huggingface_sa_{role}",
        project=gcp_pixelml_asia_east_1.project,
        role=role,
        member=huggingface_sa.email.apply(lambda email: f"serviceAccount:{email}"),
    )
