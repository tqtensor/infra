import os

import pulumi
import pulumi_kubernetes as k8s
import yaml

from resources.cloudflare import nextcloud_origin_ca_cert, nextcloud_private_key
from resources.providers import gcp_pixelml_europe_west_4
from resources.utils import encode_tls_secret_data, get_options

OPTS = get_options(
    profile="pixelml",
    region="europe-west-4",
    type="resource",
    provider="gcp",
)


nextcloud_ns = k8s.core.v1.Namespace(
    "nextcloud_ns", metadata={"name": "nextcloud"}, opts=OPTS
)

nextcloud_tls_secret = k8s.core.v1.Secret(
    "nextcloud_tls_secret",
    metadata={
        "name": "nextcloud-tls-secret",
        "namespace": nextcloud_ns.metadata["name"],
    },
    data=pulumi.Output.all(
        nextcloud_origin_ca_cert.certificate, nextcloud_private_key.private_key_pem
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = os.path.join(os.path.dirname(__file__), "values", "nextcloud.yaml")
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

nextcloud_chart = k8s.helm.v3.Chart(
    "nextcloud",
    config=k8s.helm.v3.ChartOpts(
        chart="nextcloud",
        version="6.6.3",
        fetch_opts=k8s.helm.v3.FetchOpts(repo="https://nextcloud.github.io/helm"),
        namespace=nextcloud_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=gcp_pixelml_europe_west_4,
        depends_on=[nextcloud_ns],
    ),
)
