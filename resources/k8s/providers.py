import pulumi_kubernetes as k8s

from resources.k8s.cluster.gke import auto_pilot_eu_west_4_cluster
from resources.utils import create_kubeconfig

k8s_provider_auto_pilot_eu_west_4 = k8s.Provider(
    "k8s_provider_auto_pilot_eu_west_4",
    kubeconfig=create_kubeconfig(cluster=auto_pilot_eu_west_4_cluster),
)
