from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare.tls.tqtensor_com import paper_origin_ca_cert_bundle
from resources.db.instance.paperless import (
    paperless_api_key,
    paperless_db,
    paperless_iam_app,
)
from resources.providers.k8s import k8s_par_2
from resources.utils import encode_tls_secret_data, fill_in_password
from resources.vm.networking.whitelist import whitelist_cidrs

OPTS = pulumi.ResourceOptions(provider=k8s_par_2)


paperless_ns = k8s.core.v1.Namespace(
    "paperless_ns", metadata={"name": "paperless"}, opts=OPTS
)

paperless_tls_secret = k8s.core.v1.Secret(
    "paperless_tls_secret",
    metadata={
        "name": "paper-tls-secret",
        "namespace": paperless_ns.metadata["name"],
    },
    type="kubernetes.io/tls",
    data=Output.all(
        paper_origin_ca_cert_bundle[0].certificate,
        paper_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

secrets_file_path = Path(__file__).parent / "secrets" / "paperless.yaml"

paperless_secret_key = fill_in_password(
    encrypted_yaml=str(secrets_file_path), value_path="paperless_secret_key"
)
paperless_admin_password = fill_in_password(
    encrypted_yaml=str(secrets_file_path), value_path="paperless_admin_password"
)

paperless_app_secret = k8s.core.v1.Secret(
    "paperless_app_secret",
    metadata={
        "name": "paperless-app-secret",
        "namespace": paperless_ns.metadata["name"],
    },
    string_data=Output.all(paperless_secret_key, paperless_admin_password).apply(
        lambda args: {
            "PAPERLESS_SECRET_KEY": args[0]["paperless_secret_key"],
            "PAPERLESS_ADMIN_USER": "admin",
            "PAPERLESS_ADMIN_PASSWORD": args[1]["paperless_admin_password"],
        }
    ),
    opts=OPTS,
)

paperless_db_secret = k8s.core.v1.Secret(
    "paperless_db_secret",
    metadata={
        "name": "paperless-db-secret",
        "namespace": paperless_ns.metadata["name"],
    },
    string_data=Output.all(
        paperless_db.endpoint,
        paperless_iam_app.id,
        paperless_api_key.secret_key,
    ).apply(
        lambda args: {
            "PAPERLESS_DBHOST": (
                args[0].split("://")[1].split(":")[0].split("/")[0]
                if "://" in args[0]
                else args[0].split(":")[0]
            ),
            "PAPERLESS_DBPORT": (
                args[0].split("://")[1].split(":")[1].split("/")[0]
                if "://" in args[0] and ":" in args[0].split("://")[1]
                else "5432"
            ),
            "PAPERLESS_DBNAME": "paperless",
            "PAPERLESS_DBUSER": args[1],
            "PAPERLESS_DBPASS": args[2],
            "PAPERLESS_DBSSLMODE": "require",
        }
    ),
    opts=OPTS,
)

values_file_path = Path(__file__).parent / "values" / "paperless.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

chart_values["ingress"]["main"]["annotations"][
    "nginx.ingress.kubernetes.io/whitelist-source-range"
] = Output.all(*whitelist_cidrs).apply(lambda args: ",".join(args))

paperless_release = k8s.helm.v3.Release(
    "paperless",
    k8s.helm.v3.ReleaseArgs(
        chart="paperless-ngx",
        version="0.24.1",
        name="paperless",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://charts.gabe565.com",
        ),
        namespace=paperless_ns.metadata["name"],
        values={
            **chart_values,
            "envFrom": [
                {"secretRef": {"name": "paperless-app-secret"}},
                {"secretRef": {"name": "paperless-db-secret"}},
            ],
        },
    ),
    opts=pulumi.ResourceOptions.merge(
        OPTS,
        pulumi.ResourceOptions(
            depends_on=[
                paperless_ns,
                paperless_tls_secret,
                paperless_app_secret,
                paperless_db_secret,
            ]
        ),
    ),
)
