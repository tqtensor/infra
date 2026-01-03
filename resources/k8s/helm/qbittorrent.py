from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare.tls.tqtensor_com import torrent_origin_ca_cert_bundle
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
    type="kubernetes.io/tls",
    data=Output.all(
        torrent_origin_ca_cert_bundle[0].certificate,
        torrent_origin_ca_cert_bundle[1].private_key_pem,
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
