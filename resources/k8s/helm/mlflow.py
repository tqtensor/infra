from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare.tls import mlflow_origin_ca_cert_bundle
from resources.db.psql import mlflow_auth_db, mlflow_auth_user, mlflow_db, mlflow_user
from resources.db.rds import krp_eu_central_1_rds_cluster_instance
from resources.iam.user import mlflow_access_key
from resources.k8s.providers import k8s_provider_auto_pilot_eu_west_4
from resources.storage.bucket import mlflow_bucket
from resources.utils import encode_tls_secret_data, fill_in_password

OPTS = pulumi.ResourceOptions(provider=k8s_provider_auto_pilot_eu_west_4)


mlflow_ns = k8s.core.v1.Namespace("mlflow_ns", metadata={"name": "mlflow"}, opts=OPTS)

mlflow_tls_secret = k8s.core.v1.Secret(
    "mlflow_tls_secret",
    metadata={"name": "mlflow-tls-secret", "namespace": mlflow_ns.metadata["name"]},
    data=Output.all(
        mlflow_origin_ca_cert_bundle[0].certificate,
        mlflow_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

secrets_file_path = Path(__file__).parent / "secrets" / "mlflow.yaml"
secret_values = fill_in_password(
    encrypted_yaml=secrets_file_path, value_path="adminPassword"
)

values_file_path = Path(__file__).parent / "values" / "mlflow.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    def prepare_values(
        host,
        user,
        password,
        database,
        auth_host,
        auth_user,
        auth_password,
        auth_database,
        admin_password,
        aws_access_key_id,
        aws_secret_access_key,
        bucket,
    ):
        return {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "auth_host": auth_host,
            "auth_user": auth_user,
            "auth_password": auth_password,
            "auth_database": auth_database,
            "admin_password": admin_password,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "bucket": bucket,
        }

    values = Output.all(
        krp_eu_central_1_rds_cluster_instance.endpoint,
        mlflow_user.name,
        mlflow_user.password,
        mlflow_db.name,
        krp_eu_central_1_rds_cluster_instance.endpoint,
        mlflow_auth_user.name,
        mlflow_auth_user.password,
        mlflow_auth_db.name,
        secret_values["adminPassword"],
        mlflow_access_key.id,
        mlflow_access_key.secret,
        mlflow_bucket.id,
    ).apply(
        lambda args: prepare_values(
            args[0],
            args[1],
            args[2],
            args[3],
            args[4],
            args[5],
            args[6],
            args[7],
            args[8],
            args[9],
            args[10],
            args[11],
        )
    )

    chart_values["backendStore"]["postgres"]["host"] = values["host"]
    chart_values["backendStore"]["postgres"]["user"] = values["user"]
    chart_values["backendStore"]["postgres"]["database"] = values["database"]
    chart_values["backendStore"]["postgres"]["password"] = values["password"]

    chart_values["auth"]["postgres"]["host"] = values["auth_host"]
    chart_values["auth"]["postgres"]["user"] = values["auth_user"]
    chart_values["auth"]["postgres"]["database"] = values["auth_database"]
    chart_values["auth"]["postgres"]["password"] = values["auth_password"]

    chart_values["auth"]["adminPassword"] = values["admin_password"]

    chart_values["artifactRoot"]["s3"]["awsAccessKeyId"] = values["aws_access_key_id"]
    chart_values["artifactRoot"]["s3"]["awsSecretAccessKey"] = values[
        "aws_secret_access_key"
    ]
    chart_values["artifactRoot"]["s3"]["bucket"] = values["bucket"]


mlflow_release = k8s.helm.v3.Release(
    "mlflow",
    k8s.helm.v3.ReleaseArgs(
        chart="mlflow",
        version="0.17.2",
        name="mlflow",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://community-charts.github.io/helm-charts",
        ),
        namespace=mlflow_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_auto_pilot_eu_west_4,
        depends_on=[mlflow_ns, mlflow_tls_secret],
    ),
)
