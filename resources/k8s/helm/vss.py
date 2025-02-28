import os

import pulumi
import pulumi_kubernetes as k8s
import yaml

from resources.k8s.providers import k8s_provider_asia_east_1
from resources.utils import fill_in_password

OPTS = pulumi.ResourceOptions(provider=k8s_provider_asia_east_1)


vss_ns = k8s.core.v1.Namespace("vss_ns", metadata={"name": "vss"}, opts=OPTS)

secrets_file_path = os.path.join(os.path.dirname(__file__), "secrets", "vss.yaml")
secret_values = fill_in_password(encrypted_yaml=secrets_file_path, value_path="dummy")

values_file_path = os.path.join(os.path.dirname(__file__), "values", "vss.yaml")
chart_values = yaml.safe_load(open(values_file_path, "r").read())
chart_values["vss"]["applicationSpecs"]["vss-deployment"]["containers"]["vss"][
    "env"
].append({"name": "OPENAI_API_KEY", "value": secret_values["OPENAI_API_KEY"]})
chart_values["vss"]["applicationSpecs"]["vss-deployment"]["containers"]["vss"]["image"][
    "repository"
] = "asia-east1-docker.pkg.dev/gen-lang-client-0608717027/pixeml-asia-east1-registry/nvidia/vss-engine:2.2.0"

chart_file_path = os.path.join(
    os.path.dirname(__file__), "charts", "nvidia-blueprint-vss-2.2.0.tgz"
)
vss_release = k8s.helm.v3.Release(
    "nvidia-blueprint-vss",
    k8s.helm.v3.ReleaseArgs(
        chart=chart_file_path,
        name="nvidia-blueprint-vss",
        namespace=vss_ns.metadata["name"],
        values=chart_values,
        version="2.2.0",
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_asia_east_1,
        depends_on=[vss_ns],
    ),
)
