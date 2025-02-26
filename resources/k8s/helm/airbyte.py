import base64
import os

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare import airbyte_origin_ca_cert, airbyte_private_key
from resources.db import airbyte_db, airbyte_user, krp_ec1_rds_cluster_instance
from resources.providers import gcp_pixelml_europe_west_4
from resources.utils import encode_tls_secret_data, get_options

OPTS = get_options(
    profile="pixelml",
    region="europe-west-4",
    type="resource",
    provider="gcp",
)


airbyte_ns = k8s.core.v1.Namespace(
    "airbyte_ns", metadata={"name": "airbyte"}, opts=OPTS
)

airbyte_config_secrets = k8s.core.v1.Secret(
    "airbyte_config_secrets",
    metadata={
        "name": "airbyte-config-secrets",
        "namespace": airbyte_ns.metadata["name"],
    },
    data=Output.all(airbyte_user.password).apply(
        lambda args: {
            "database-password": base64.b64encode(args[0].encode()).decode(),
        }
    ),
    opts=OPTS,
)

airbyte_tls_secret = k8s.core.v1.Secret(
    "airbyte_tls_secret",
    metadata={"name": "airbyte-tls-secret", "namespace": airbyte_ns.metadata["name"]},
    data=Output.all(
        airbyte_origin_ca_cert.certificate, airbyte_private_key.private_key_pem
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = os.path.join(os.path.dirname(__file__), "values", "airbyte.yaml")
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    def prepare_values(host, user, database):
        return {
            "host": host,
            "user": user,
            "database": database,
        }

    values = Output.all(
        krp_ec1_rds_cluster_instance.endpoint,
        airbyte_user.name,
        airbyte_db.name,
    ).apply(lambda args: prepare_values(args[0], args[1], args[2]))

    chart_values["global"]["database"]["host"] = values["host"]
    chart_values["global"]["database"]["user"] = values["user"]
    chart_values["global"]["database"]["database"] = values["database"]

airbyte_release = k8s.helm.v3.Release(
    "airbyte",
    k8s.helm.v3.ReleaseArgs(
        chart="airbyte",
        version="1.5.0",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://airbytehq.github.io/helm-charts",
        ),
        namespace=airbyte_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=gcp_pixelml_europe_west_4,
        depends_on=[airbyte_ns],
    ),
)
