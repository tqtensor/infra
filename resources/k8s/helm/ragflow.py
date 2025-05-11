from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare.tls import ragflow_origin_ca_cert, ragflow_private_key
from resources.k8s.providers import k8s_provider_auto_pilot_eu_west_4
from resources.utils import encode_tls_secret_data

OPTS = pulumi.ResourceOptions(provider=k8s_provider_auto_pilot_eu_west_4)


ragflow_ns = k8s.core.v1.Namespace(
    "ragflow_ns", metadata={"name": "ragflow"}, opts=OPTS
)

ragflow_sa = k8s.core.v1.ServiceAccount(
    "ragflow_sa",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="ragflow",
        namespace=ragflow_ns.metadata["name"],
    ),
    opts=OPTS,
)

ragflow_tls_secret = k8s.core.v1.Secret(
    "ragflow_tls_secret",
    metadata={"name": "ragflow-tls-secret", "namespace": ragflow_ns.metadata["name"]},
    data=Output.all(
        ragflow_origin_ca_cert.certificate, ragflow_private_key.private_key_pem
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = Path(__file__).parent / "values" / "ragflow.yaml"
if values_file_path.exists():
    chart_values = yaml.safe_load(open(values_file_path, "r").read())

chart_file_path = str(Path(__file__).parent / "charts" / "ragflow-0.1.0.tgz")
ragflow_release = k8s.helm.v3.Release(
    "ragflow",
    k8s.helm.v3.ReleaseArgs(
        chart=chart_file_path,
        name="ragflow",
        namespace=ragflow_ns.metadata["name"],
        values=chart_values,
        version="0.1.0",
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_auto_pilot_eu_west_4,
        depends_on=[ragflow_ns],
    ),
)
