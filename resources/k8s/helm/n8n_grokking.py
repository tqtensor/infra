import os

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare import (
    grokking_origin_ca_cert,
    grokking_private_key,
    grokking_tqtensor_com,
)
from resources.db import (
    krp_ec1_rds_cluster_instance,
    n8n_grokking_db,
    n8n_grokking_user,
)
from resources.providers import gcp_pixelml_europe_west_4
from resources.utils import encode_tls_secret_data, get_options

OPTS = get_options(
    profile="pixelml",
    region="europe-west-4",
    type="resource",
    provider="gcp",
)


n8n_grokking_ns = k8s.core.v1.Namespace(
    "n8n_grokking_ns", metadata={"name": "n8n-grokking"}, opts=OPTS
)

n8n_grokking_tls_secret = k8s.core.v1.Secret(
    "n8n_grokking_tls_secret",
    metadata={"name": "n8n-tls-secret", "namespace": n8n_grokking_ns.metadata["name"]},
    data=Output.all(
        grokking_origin_ca_cert.certificate, grokking_private_key.private_key_pem
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = os.path.join(os.path.dirname(__file__), "values", "n8n.yaml")
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    def prepare_values(host, user, password, database, domain, tls_secret_name):
        return {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "domain": domain,
            "tls_secret_name": tls_secret_name,
        }

    values = Output.all(
        krp_ec1_rds_cluster_instance.endpoint,
        n8n_grokking_user.name,
        n8n_grokking_user.password,
        n8n_grokking_db.name,
        grokking_tqtensor_com.hostname,
        n8n_grokking_tls_secret.metadata["name"],
    ).apply(
        lambda args: prepare_values(
            args[0], args[1], args[2], args[3], args[4], args[5]
        )
    )

    chart_values["config"]["database"]["postgresdb"]["host"] = values["host"]
    chart_values["config"]["database"]["postgresdb"]["user"] = values["user"]
    chart_values["secret"]["database"]["postgresdb"]["password"] = values["password"]
    chart_values["config"]["database"]["postgresdb"]["database"] = values["database"]
    chart_values["extraEnv"]["WEBHOOK_URL"] = values["domain"]
    chart_values["ingress"]["hosts"][0]["host"] = values["domain"]
    chart_values["ingress"]["tls"][0]["hosts"][0] = values["domain"]
    chart_values["ingress"]["tls"][0]["secretName"] = values["tls_secret_name"]

chart_file_path = os.path.join(os.path.dirname(__file__), "charts", "n8n-0.25.2.tgz")
n8n_grokking_release = k8s.helm.v3.Release(
    "n8n-grokking",
    k8s.helm.v3.ReleaseArgs(
        chart=chart_file_path,
        namespace=n8n_grokking_ns.metadata["name"],
        values=chart_values,
        version="0.25.2",
    ),
    opts=pulumi.ResourceOptions(
        provider=gcp_pixelml_europe_west_4,
        depends_on=[n8n_grokking_ns, n8n_grokking_tls_secret],
    ),
)
