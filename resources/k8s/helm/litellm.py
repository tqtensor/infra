import os

import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare import litellm_origin_ca_cert, litellm_private_key
from resources.iam import vertex_sa
from resources.providers import gcp_pixelml_europe_west_4, k8s_provider
from resources.utils import encode_tls_secret_data, fill_in_password, get_options

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
    data=Output.all(
        litellm_origin_ca_cert.certificate, litellm_private_key.private_key_pem
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

litellm_sa = k8s.core.v1.ServiceAccount(
    "litellm_sa",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="litellm",
        annotations={"iam.gke.io/gcp-service-account": vertex_sa.email},
        namespace=litellm_ns.metadata["name"],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

litellm_iam_member = gcp.serviceaccount.IAMMember(
    "litellm_iam_member",
    service_account_id=vertex_sa.name,
    role="roles/iam.workloadIdentityUser",
    member=Output.concat(
        "serviceAccount:",
        gcp_pixelml_europe_west_4.project,
        ".svc.id.goog[",
        litellm_sa.metadata.namespace,
        "/",
        litellm_sa.metadata.name,
        "]",
    ),
)

secrets_file_path = os.path.join(os.path.dirname(__file__), "secrets", "litellm.yaml")
secret_values = fill_in_password(
    encrypted_yaml=secrets_file_path, value_path="masterkey"
)

values_file_path = os.path.join(os.path.dirname(__file__), "values", "litellm.yaml")
chart_values = yaml.safe_load(open(values_file_path, "r").read())
chart_values["masterkey"] = secret_values["masterkey"]

chart_file_path = os.path.join(
    os.path.dirname(__file__), "charts", "litellm-helm-0.3.0.tgz"
)
litellm_release = k8s.helm.v3.Release(
    "litellm-proxy",
    k8s.helm.v3.ReleaseArgs(
        chart=chart_file_path,
        namespace=litellm_ns.metadata["name"],
        values=chart_values,
        version="0.3.0",
    ),
    opts=pulumi.ResourceOptions(
        provider=gcp_pixelml_europe_west_4,
        depends_on=[litellm_ns, litellm_tls_secret],
    ),
)
