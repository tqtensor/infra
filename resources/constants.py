"""
Avoids accidental delete of resources or circular dependencies.
"""

import pulumi_cloudflare as cloudflare
import pulumi_gcp as gcp
import pulumiverse_scaleway as scw

# Cloudflare
tqtensor_com: cloudflare.Zone = cloudflare.Zone.get(
    "tqtensor_com",
    id="1fa667eb57e3e586d4f0bd8b6cd2e7ad",
)

# GCP
netherlands_ts_external_ip: gcp.compute.Address = gcp.compute.Address.get(
    "netherlands_ts_external_ip",
    id="ts-nld-external-ip",
    region="europe-west4",
    project="gen-lang-client-0608717027",
)

# Scaleway
par_2_cluster: scw.kubernetes.Cluster = scw.kubernetes.Cluster.get(
    "par_2_cluster",
    id="fr-par/773f9f89-6cf5-44d9-b427-667dea748098",
)

nginx_ip_par_2 = scw.loadbalancers.Ip.get(
    "nginx_ip_par_2",
    id="fr-par-2/c8bbfacd-0e90-4297-a45a-0bbe30abceb3",
)
