from pathlib import Path
from typing import Union

import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
import pulumiverse_scaleway as sw
import yaml

from resources.k8s import nginx_lb_par_2
from resources.k8s.providers import (
    k8s_provider_auto_pilot_eu_west_4,
    k8s_provider_par_2,
)
from resources.vm import nginx_ip_eu_west_4


def deploy_nginx(
    region: str,
    provider: k8s.Provider,
    public_ip: Union[gcp.compute.Address, sw.loadbalancers.LoadBalancer],
):
    opts = pulumi.ResourceOptions(
        provider=provider,
    )

    nginx_ns = k8s.core.v1.Namespace(
        "nginx_ns_{}".format(region.replace("-", "_")),
        metadata={"name": "ingress-nginx"},
        opts=opts,
    )

    values_file_path = Path(__file__).parent / "values" / "nginx.yaml"
    with open(values_file_path, "r") as f:
        chart_values = yaml.safe_load(f)
        if isinstance(public_ip, gcp.compute.Address):
            chart_values["controller"]["service"]["loadBalancerIP"] = public_ip.address
        elif isinstance(public_ip, sw.loadbalancers.LoadBalancer):
            del chart_values["controller"]["service"]["loadBalancerIP"]
            chart_values["controller"]["service"]["annotations"] = {
                "service.beta.kubernetes.io/scw-loadbalancer-id": public_ip.id
            }
        else:
            raise ValueError("Invalid public_ip type")

    _ = k8s.helm.v3.Release(
        f"ingress-nginx-{region}",
        k8s.helm.v3.ReleaseArgs(
            chart="ingress-nginx",
            name="ingress-nginx",
            version="4.12.0",
            repository_opts=k8s.helm.v3.RepositoryOptsArgs(
                repo="https://kubernetes.github.io/ingress-nginx",
            ),
            namespace=nginx_ns.metadata["name"],
            values=chart_values,
        ),
        opts=pulumi.ResourceOptions(
            provider=provider,
            depends_on=[nginx_ns],
        ),
    )


deploy_nginx(
    region="eu-west-4",
    provider=k8s_provider_auto_pilot_eu_west_4,
    public_ip=nginx_ip_eu_west_4,
)

deploy_nginx(
    region="par-2",
    provider=k8s_provider_par_2,
    public_ip=nginx_lb_par_2,
)
