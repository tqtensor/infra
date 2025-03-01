import base64

import pulumi
import pulumi_gcp as gcp
from pulumi import Output

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

vertex_sa_key = gcp.serviceaccount.Key(
    "vertex_sa_key",
    service_account_id=vertex_sa.name,
    public_key_type="TYPE_X509_PEM_FILE",
    opts=OPTS,
)

decoded_private_key = vertex_sa_key.private_key.apply(
    lambda key: base64.b64decode(key).decode("utf-8")
)

pulumi.export("IAM: Vertex: SA", Output.secret(decoded_private_key))
