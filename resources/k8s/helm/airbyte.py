import base64
from pathlib import Path
from typing import Dict

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare.tls import airbyte_origin_ca_cert_bundle
from resources.constants import cpu_pool_par_2
from resources.db.instance import psql_par_1_instance
from resources.db.psql import airbyte_db, airbyte_user
from resources.k8s.providers import k8s_provider_par_2
from resources.utils import encode_tls_secret_data

OPTS = pulumi.ResourceOptions(provider=k8s_provider_par_2)


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
        airbyte_origin_ca_cert_bundle[0].certificate,
        airbyte_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = Path(__file__).parent / "values" / "airbyte.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    def prepare_values(
        host: str, port: int, user: str, database: str
    ) -> Dict[str, str]:
        return {
            "host": host,
            "port": port,
            "user": user,
            "database": database,
        }

    def set_node_selector(config, selector):
        if isinstance(config, dict):
            if "nodeSelector" in config:
                config["nodeSelector"] = selector
            for v in config.values():
                set_node_selector(v, selector)
        elif isinstance(config, list):
            for item in config:
                set_node_selector(item, selector)

    def set_resources(config, resources):
        if isinstance(config, dict):
            if "resources" in config:
                config["resources"] = resources
            for v in config.values():
                set_resources(v, resources)
        elif isinstance(config, list):
            for item in config:
                set_resources(item, resources)

    values = Output.all(
        psql_par_1_instance.load_balancers[0].ip,
        psql_par_1_instance.load_balancers[0].port,
        airbyte_user.name,
        airbyte_db.name,
    ).apply(lambda args: prepare_values(args[0], args[1], args[2], args[3]))

    chart_values["global"]["database"]["host"] = values["host"]
    chart_values["global"]["database"]["port"] = values["port"]
    chart_values["global"]["database"]["user"] = values["user"]
    chart_values["global"]["database"]["database"] = values["database"]

    set_node_selector(
        config=chart_values,
        selector=Output.all(cpu_pool_par_2.name).apply(
            lambda args: {
                "k8s.scaleway.com/pool-name": args[0],
            }
        ),
    )

    set_resources(
        config=chart_values,
        resources={
            "requests": {
                "cpu": "250m",
                "memory": "256Mi",
            }
        },
    )

airbyte_release = k8s.helm.v3.Release(
    "airbyte",
    k8s.helm.v3.ReleaseArgs(
        chart="airbyte",
        version="1.6.1",
        name="airbyte",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://airbytehq.github.io/helm-charts",
        ),
        namespace=airbyte_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_par_2,
        depends_on=[airbyte_ns],
    ),
)
