import os
from pathlib import Path

import pandas as pd
import pulumi
import pulumi_cloudflare as cloudflare
import pulumi_kubernetes as k8s
import pulumi_postgresql as postgresql
import pulumi_tls as tls
import yaml
from pulumi import Output

from resources.cloudflare import *  # noqa
from resources.db import krp_ec1_rds_cluster_instance
from resources.db.psql import *  # noqa
from resources.k8s.providers import k8s_provider_eu_west_4
from resources.utils import encode_tls_secret_data, normalize_email

OPTS = pulumi.ResourceOptions(provider=k8s_provider_eu_west_4)


def deploy_n8n(
    username: str,
    db: postgresql.Database,
    db_user: postgresql.Role,
    domain: cloudflare.Record,
    origin_ca_cert: cloudflare.OriginCaCertificate,
    private_key: tls.PrivateKey,
):
    ns = k8s.core.v1.Namespace(
        f"n8n_{username}_ns", metadata={"name": f"n8n-{username}"}, opts=OPTS
    )

    tls_secret = k8s.core.v1.Secret(
        f"n8n_{username}_tls_secret",
        metadata={
            "name": "n8n-tls-secret",
            "namespace": ns.metadata["name"],
        },
        data=Output.all(origin_ca_cert.certificate, private_key.private_key_pem).apply(
            lambda args: encode_tls_secret_data(args[0], args[1])
        ),
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
            db_user.name,
            db_user.password,
            db.name,
            domain.hostname,
            tls_secret.metadata["name"],
        ).apply(
            lambda args: prepare_values(
                args[0], args[1], args[2], args[3], args[4], args[5]
            )
        )

        chart_values["config"]["database"]["postgresdb"]["host"] = values["host"]
        chart_values["config"]["database"]["postgresdb"]["user"] = values["user"]
        chart_values["secret"]["database"]["postgresdb"]["password"] = values[
            "password"
        ]
        chart_values["config"]["database"]["postgresdb"]["database"] = values[
            "database"
        ]
        chart_values["extraEnv"]["WEBHOOK_URL"] = values["domain"]
        chart_values["ingress"]["hosts"][0]["host"] = values["domain"]
        chart_values["ingress"]["tls"][0]["hosts"][0] = values["domain"]
        chart_values["ingress"]["tls"][0]["secretName"] = values["tls_secret_name"]

    chart_file_path = os.path.join(
        os.path.dirname(__file__), "charts", "n8n-0.25.2.tgz"
    )
    release = k8s.helm.v3.Release(
        f"n8n-{username}",
        k8s.helm.v3.ReleaseArgs(
            chart=chart_file_path,
            name="n8n",
            namespace=ns.metadata["name"],
            values=chart_values,
            version="0.25.2",
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider_eu_west_4,
            depends_on=[ns, tls_secret],
            protect=False,
        ),
    )
    return release


# AWS Workshop
participants = [
    normalize_email(email=email)
    for email in pd.read_csv(
        os.path.join(
            Path(__file__).parent.parent.parent.parent, "artifacts", "participants.csv"
        )
    )["email"].values
]

for participant in participants:
    username = participant.split("@")[0]
    exec(
        f"""
n8n_{username}_release = deploy_n8n(
    username=username,
    db=n8n_{username}_db,
    db_user=n8n_{username}_user,
    domain={username}_tqtensor_com,
    origin_ca_cert=n8n_{username}_origin_ca_cert,
    private_key=n8n_{username}_private_key,
)
"""
    )
