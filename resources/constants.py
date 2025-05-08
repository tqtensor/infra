"""
Avoids accidental delete of resources or circular dependencies.
"""

import pulumi
import pulumi_cloudflare as cloudflare
import pulumi_gcp as gcp
import pulumiverse_scaleway as scw

from resources.providers import gcp_pixelml_us_central_1

# Cloudflare
krypfolio_com = cloudflare.Zone.get(
    "krypfolio_com",
    id="04f429cac6262bf28db5731a84fde86a",
    account_id=pulumi.Config().require("accountId"),
)
mservice_dev = cloudflare.Zone.get(
    "mservice_dev",
    id="2a103726472fbfdf5fe1a6ba2121c723",
    account_id=pulumi.Config().require("accountId"),
)
tqtensor_com = cloudflare.Zone.get(
    "tqtensor_com",
    id="1fa667eb57e3e586d4f0bd8b6cd2e7ad",
    account_id=pulumi.Config().require("accountId"),
)
unifai_dev = cloudflare.Zone.get(
    "unifai_dev",
    id="e37a9e60005d57df4859fa4817c8128a",
    account_id=pulumi.Config().require("accountId"),
)

# GCP
ind_cloudrun_sa = gcp.serviceaccount.Account.get(
    "ind_cloudrun_sa",
    id="projects/gen-lang-client-0608717027/serviceAccounts/cloudrun-sa-us-central-1@gen-lang-client-0608717027.iam.gserviceaccount.com",
    project=gcp_pixelml_us_central_1.project,
)

# Scaleway
ind_nginx_ip_par_2 = scw.loadbalancers.Ip.get(
    "ind_nginx_ip_par_2",
    id="fr-par-2/bfe06b07-8bf4-4568-bf50-6813edbd3cc1",
)
