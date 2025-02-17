import os

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare import n8n_origin_ca_cert, n8n_private_key
from resources.db import krp_ec1_rds_cluster_instance, n8n_dolphin_db, n8n_dolphin_user
from resources.providers import gcp_pixelml_europe_west_4
from resources.utils import encode_tls_secret_data, get_options

OPTS = get_options(
    profile="pixelml",
    region="europe-west-4",
    type="resource",
    provider="gcp",
    protect=False,
)


n8n_ns = k8s.core.v1.Namespace("n8n_ns", metadata={"name": "n8n"}, opts=OPTS)

n8n_tls_secret = k8s.core.v1.Secret(
    "n8n_tls_secret",
    metadata={"name": "n8n-tls-secret", "namespace": n8n_ns.metadata["name"]},
    data=Output.all(
        n8n_origin_ca_cert.certificate, n8n_private_key.private_key_pem
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = os.path.join(os.path.dirname(__file__), "values", "n8n.yaml")
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    def prepare_db_values(host, user, password, database):
        return {"host": host, "user": user, "password": password, "database": database}

    db_values = Output.all(
        krp_ec1_rds_cluster_instance.endpoint,
        n8n_dolphin_user.name,
        n8n_dolphin_user.password,
        n8n_dolphin_db.name,
    ).apply(lambda args: prepare_db_values(args[0], args[1], args[2], args[3]))

    chart_values["config"]["database"]["postgresdb"]["host"] = db_values["host"]
    chart_values["config"]["database"]["postgresdb"]["user"] = db_values["user"]
    chart_values["secret"]["database"]["postgresdb"]["password"] = db_values["password"]
    chart_values["config"]["database"]["postgresdb"]["database"] = db_values["database"]

chart_file_path = os.path.join(os.path.dirname(__file__), "charts", "n8n-0.25.2.tgz")
n8n_release = k8s.helm.v3.Release(
    "n8n",
    k8s.helm.v3.ReleaseArgs(
        chart=chart_file_path,
        namespace=n8n_ns.metadata["name"],
        values=chart_values,
        version="0.25.2",
    ),
    opts=pulumi.ResourceOptions(
        provider=gcp_pixelml_europe_west_4,
        depends_on=[n8n_ns, n8n_tls_secret],
        protect=True,
    ),
)
