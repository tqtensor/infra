import pulumi_kubernetes as k8s

from resources.constants import cluster_par_2
from resources.utils import create_kubeconfig

k8s_provider_par_2 = k8s.Provider(
    "k8s_provider_par_2",
    kubeconfig=create_kubeconfig(cluster=cluster_par_2),
)
