import os

import pulumi
import pulumi_kubernetes as k8s
import yaml

from resources.cloudflare import n8n_origin_ca_cert, n8n_private_key
from resources.providers import gcp_pixelml_europe_west_4
from resources.utils import encode_tls_secret_data, get_options

OPTS = get_options(
    profile="pixelml",
    region="europe-west-4",
    type="resource",
    provider="gcp",
)


n8n_ns = k8s.core.v1.Namespace("n8n_ns", metadata={"name": "n8n"}, opts=OPTS)

n8n_tls_secret = k8s.core.v1.Secret(
    "n8n_tls_secret",
    metadata={"name": "n8n-tls-secret", "namespace": n8n_ns.metadata["name"]},
    data=pulumi.Output.all(
        n8n_origin_ca_cert.certificate, n8n_private_key.private_key_pem
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = os.path.join(os.path.dirname(__file__), "values", "n8n.yaml")
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

chart_file_path = os.path.join(os.path.dirname(__file__), "n8n-0.25.2.tgz")
n8n_chart = k8s.helm.v3.Chart(
    "n8n",
    config=k8s.helm.v3.LocalChartOpts(
        path=chart_file_path,
        namespace=n8n_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=gcp_pixelml_europe_west_4,
        depends_on=[n8n_ns],
    ),
)
