import os

import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
import yaml

from resources.k8s.cluster import (
    auto_pilot_asia_east_1_cluster,
    auto_pilot_eu_west_4_cluster,
)
from resources.utils import create_kubeconfig
from resources.vm import nginx_ip_asia_east_1, nginx_ip_eu_west_4


def deploy_nginx(
    region: str, cluster: gcp.container.Cluster, public_ip: gcp.compute.Address
):
    k8s_provider = k8s.Provider(
        "k8s_provider_{}".format(region.replace("-", "_")),
        kubeconfig=create_kubeconfig(cluster=cluster),
    )

    opts = pulumi.ResourceOptions(
        provider=k8s_provider,
    )

    nginx_ns = k8s.core.v1.Namespace(
        "nginx_ns_{}".format(region.replace("-", "_")),
        metadata={"name": "ingress-nginx"},
        opts=opts,
    )

    values_file_path = os.path.join(os.path.dirname(__file__), "values", "nginx.yaml")
    with open(values_file_path, "r") as f:
        chart_values = yaml.safe_load(f)
        chart_values["controller"]["service"]["loadBalancerIP"] = public_ip.address

    _ = k8s.helm.v3.Release(
        f"ingress-nginx-{region}",
        k8s.helm.v3.ReleaseArgs(
            chart="ingress-nginx",
            version="4.12.0",
            repository_opts=k8s.helm.v3.RepositoryOptsArgs(
                repo="https://kubernetes.github.io/ingress-nginx",
            ),
            namespace=nginx_ns.metadata["name"],
            values=chart_values,
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[nginx_ns],
        ),
    )


deploy_nginx(
    region="asia-east-1",
    cluster=auto_pilot_asia_east_1_cluster,
    public_ip=nginx_ip_asia_east_1,
)
deploy_nginx(
    region="europe-west-4",
    cluster=auto_pilot_eu_west_4_cluster,
    public_ip=nginx_ip_eu_west_4,
)
