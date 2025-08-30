"""
Avoids accidental delete of resources or circular dependencies.
"""

import pulumi
import pulumi_aws as aws
import pulumi_cloudflare as cloudflare
import pulumiverse_scaleway as scw

from resources.utils import get_options

# AWS
stx_iam_user = aws.iam.User.get(
    "stx_iam_user",
    id="thaitang",
    opts=get_options(profile="stx", region="us-east-1", type="resource"),
)

# Cloudflare
krypfolio_com = cloudflare.Zone.get(
    "krypfolio_com",
    id="04f429cac6262bf28db5731a84fde86a",
    account_id=pulumi.Config().require("cloudflareAccountId"),
)
mservice_dev = cloudflare.Zone.get(
    "mservice_dev",
    id="2a103726472fbfdf5fe1a6ba2121c723",
    account_id=pulumi.Config().require("cloudflareAccountId"),
)
tqtensor_com = cloudflare.Zone.get(
    "tqtensor_com",
    id="1fa667eb57e3e586d4f0bd8b6cd2e7ad",
    account_id=pulumi.Config().require("cloudflareAccountId"),
)
unifai_dev = cloudflare.Zone.get(
    "unifai_dev",
    id="e37a9e60005d57df4859fa4817c8128a",
    account_id=pulumi.Config().require("cloudflareAccountId"),
)

# Scaleway
cluster_par_2 = scw.kubernetes.Cluster.get(
    "cluster_par_2",
    id="fr-par/773f9f89-6cf5-44d9-b427-667dea748098",
)

cpu_pool_par_2 = scw.kubernetes.Pool.get(
    "cpu_pool_par_2",
    id="fr-par/ae07f0f5-3a98-4ed0-b4b3-121f45656bc1",
)

l4_pool_par_2 = scw.kubernetes.Pool.get(
    "l4_pool_par_2",
    id="fr-par/65d0776e-bfc0-496e-8e87-a0ff2641ca2e",
)

l40s_pool_par_2 = scw.kubernetes.Pool.get(
    "l40s_pool_par_2",
    id="fr-par/5887b352-5153-4871-8ef3-12a6d3df2156",
)

nginx_ip_par_2 = scw.loadbalancers.Ip.get(
    "nginx_ip_par_2",
    id="fr-par-2/c8bbfacd-0e90-4297-a45a-0bbe30abceb3",
)
