from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
from pulumi import Output

from resources.cloudflare import s3_origin_ca_cert, s3_private_key
from resources.k8s.providers import k8s_provider_par_2
from resources.utils import encode_tls_secret_data

OPTS = pulumi.ResourceOptions(provider=k8s_provider_par_2)


s3_tls_secret = k8s.core.v1.Secret(
    "s3_tls_secret",
    metadata={"name": "s3-tls-secret", "namespace": "noobaa"},
    data=Output.all(
        s3_origin_ca_cert.certificate, s3_private_key.private_key_pem
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

ingress_yaml_path = str(Path(__file__).parent / "artifacts" / "ingress.yaml")
noobaa_s3_ingress = k8s.yaml.ConfigFile(
    "noobaa_s3_ingress",
    file=ingress_yaml_path,
    opts=OPTS,
)
