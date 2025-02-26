import os

import pulumi
import pulumi_kubernetes as k8s
import yaml

from resources.providers import gcp_pixelml_europe_west_4
from resources.utils import get_options
from resources.vm import nginx_ip_eu_west_4

OPTS = get_options(
    profile="pixelml",
    region="europe-west-4",
    type="resource",
    provider="gcp",
)


nginx_ns = k8s.core.v1.Namespace(
    "nginx_ns", metadata={"name": "ingress-nginx"}, opts=OPTS
)

values_file_path = os.path.join(os.path.dirname(__file__), "values", "nginx.yaml")
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)
    chart_values["controller"]["service"]["loadBalancerIP"] = nginx_ip_eu_west_4.address

nginx_release = k8s.helm.v3.Release(
    "ingress-nginx",
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
        provider=gcp_pixelml_europe_west_4,
        depends_on=[nginx_ns],
    ),
)
