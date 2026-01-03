import pulumi_kubernetes as k8s

from resources import constants

# Scaleway par-2 cluster
k8s_par_2 = k8s.Provider(
    "k8s_par_2",
    kubeconfig=constants.par_2_cluster.kubeconfigs[0].config_file,
)
