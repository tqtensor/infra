import os

import pulumi
import pulumi_kubernetes as k8s
from sopsy import Sops

from resources.cloudflare import litellm_origin_ca_cert, litellm_private_key
from resources.providers import gcp_pixelml_europe_west_4
from resources.utils import encode_tls_secret_data, get_options

OPTS = get_options(
    profile="pixelml",
    region="europe-west-4",
    type="resource",
    provider="gcp",
)


litellm_ns = k8s.core.v1.Namespace(
    "litellm_ns", metadata={"name": "litellm"}, opts=OPTS
)

litellm_tls_secret = k8s.core.v1.Secret(
    "litellm_tls_secret",
    metadata={"name": "litellm-tls-secret", "namespace": litellm_ns.metadata["name"]},
    data=pulumi.Output.all(
        litellm_origin_ca_cert.certificate, litellm_private_key.private_key_pem
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = os.path.join(os.path.dirname(__file__), "values", "litellm.yaml")
sops = Sops(values_file_path)
try:
    chart_values = sops.decrypt()
except Exception as e:
    pulumi.log.error(f"Failed to decrypt {values_file_path}: {e}")
    raise

chart_file_path = os.path.join(os.path.dirname(__file__), "litellm-helm-0.3.0.tgz")
litellm_chart = k8s.helm.v3.Chart(
    "litellm-proxy",
    config=k8s.helm.v3.LocalChartOpts(
        path=chart_file_path,
        namespace=litellm_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=gcp_pixelml_europe_west_4,
        depends_on=[litellm_ns, litellm_tls_secret],
    ),
)
