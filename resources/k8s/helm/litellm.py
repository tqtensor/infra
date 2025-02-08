import os

import pulumi
import pulumi_kubernetes as k8s
from sopsy import Sops

from resources.providers import gcp_pixelml_europe_west_4
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="europe-west-4", type="resource", provider="gcp"
)


litellm_ns = k8s.core.v1.Namespace(
    "litellm_ns", metadata={"name": "litellm"}, opts=OPTS
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
        provider=gcp_pixelml_europe_west_4, depends_on=[litellm_ns], protect=False
    ),
)
