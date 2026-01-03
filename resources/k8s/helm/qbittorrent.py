from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare.tls.tqtensor_com import (
    torrent_origin_ca_cert,
    torrent_private_key,
)
from resources.providers.k8s import k8s_par_2
from resources.utils import encode_tls_secret_data

OPTS = pulumi.ResourceOptions(provider=k8s_par_2)


qbittorrent_ns = k8s.core.v1.Namespace(
    "qbittorrent_ns", metadata={"name": "torrent"}, opts=OPTS
)

qbittorrent_tls_secret = k8s.core.v1.Secret(
    "qbittorrent_tls_secret",
    metadata={
        "name": "torrent-tls-secret",
        "namespace": qbittorrent_ns.metadata["name"],
    },
    data=Output.all(
        torrent_origin_ca_cert.certificate,
        torrent_private_key.private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = Path(__file__).parent / "values" / "qbittorrent.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

qbittorrent_release = k8s.helm.v3.Release(
    "qbittorrent",
    k8s.helm.v3.ReleaseArgs(
        chart="qbittorrent",
        version="0.4.1",
        name="qbittorrent",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://gabe565.github.io/charts",
        ),
        namespace=qbittorrent_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions.merge(
        OPTS,
        pulumi.ResourceOptions(depends_on=[qbittorrent_ns, qbittorrent_tls_secret]),
    ),
)

# Custom Ingress resource with TLS
qbittorrent_ingress = k8s.networking.v1.Ingress(
    "qbittorrent-ingress",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="qbittorrent-ingress",
        namespace=qbittorrent_ns.metadata["name"],
        annotations={
            "kubernetes.io/ingress.class": "nginx",
            "nginx.ingress.kubernetes.io/backend-protocol": "HTTP",
            "nginx.ingress.kubernetes.io/ssl-redirect": "true",
        },
    ),
    spec=k8s.networking.v1.IngressSpecArgs(
        ingress_class_name="nginx",
        tls=[
            k8s.networking.v1.IngressTLSArgs(
                hosts=["torrent.tqtensor.com"],
                secret_name="torrent-tls-secret",
            )
        ],
        rules=[
            k8s.networking.v1.IngressRuleArgs(
                host="torrent.tqtensor.com",
                http=k8s.networking.v1.HTTPIngressRuleValueArgs(
                    paths=[
                        k8s.networking.v1.HTTPIngressPathArgs(
                            path="/",
                            path_type="Prefix",
                            backend=k8s.networking.v1.IngressBackendArgs(
                                service=k8s.networking.v1.IngressServiceBackendArgs(
                                    name="qbittorrent",
                                    port=k8s.networking.v1.ServiceBackendPortArgs(
                                        number=8080,
                                    ),
                                ),
                            ),
                        )
                    ],
                ),
            )
        ],
    ),
    opts=pulumi.ResourceOptions.merge(
        OPTS,
        pulumi.ResourceOptions(depends_on=[qbittorrent_release]),
    ),
)
