import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_2nd_eu_west_4, gcp_pixelml_eu_west_4
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="eu-west-4", type="resource", provider="gcp"
)
OPTS_2ND = get_options(
    profile="pixelml_2nd", region="eu-west-4", type="resource", provider="gcp"
)


vertex_sa = gcp.serviceaccount.Account(
    "vertex_sa",
    account_id="vertex-sa-eu-west-4",
    display_name="Vertex AI Service Account",
    opts=OPTS,
)

vertex_sa_2nd = gcp.serviceaccount.Account(
    "vertex_sa_2nd",
    account_id="vertex-sa-eu-west-4",
    display_name="Vertex AI Service Account",
    opts=OPTS_2ND,
)

roles = [
    "roles/aiplatform.user",
    "roles/storage.objectViewer",
]
for role in roles:
    gcp.projects.IAMMember(
        f"vertex_sa_{role}",
        project=gcp_pixelml_eu_west_4.project,
        role=role,
        member=vertex_sa.email.apply(lambda email: f"serviceAccount:{email}"),
    )
    gcp.projects.IAMMember(
        f"vertex_sa_2nd_{role}",
        project=gcp_pixelml_2nd_eu_west_4.project,
        role=role,
        member=vertex_sa_2nd.email.apply(lambda email: f"serviceAccount:{email}"),
    )

vertex_sa_key = gcp.serviceaccount.Key(
    "vertex_sa_key",
    service_account_id=vertex_sa.name,
    public_key_type="TYPE_X509_PEM_FILE",
    opts=OPTS,
)

vertex_sa_key_2nd = gcp.serviceaccount.Key(
    "vertex_sa_key_2nd",
    service_account_id=vertex_sa_2nd.name,
    public_key_type="TYPE_X509_PEM_FILE",
    opts=OPTS_2ND,
)
