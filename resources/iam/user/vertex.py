import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_europe_west_4
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="europe-west-4", type="resource", provider="gcp"
)


vertex_sa = gcp.serviceaccount.Account(
    "vertex_sa",
    account_id="vertex-sa-europe-west-4",
)

roles = [
    "roles/aiplatform.user",
    "roles/storage.objectViewer",
]
for role in roles:
    gcp.projects.IAMMember(
        f"vertex_sa_{role}",
        project=gcp_pixelml_europe_west_4.project,
        role=role,
        member=vertex_sa.email.apply(lambda email: f"serviceAccount:{email}"),
    )
