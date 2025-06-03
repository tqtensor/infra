from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
import pulumi_random as random
import yaml
from pulumi import Output

from resources.cloudflare.record import n8n_tqtensor_com
from resources.cloudflare.tls import n8n_origin_ca_cert_bundle
from resources.db.instance import psql_par_1_instance
from resources.db.psql import n8n_dolphin_db, n8n_dolphin_user
from resources.k8s.providers import k8s_provider_auto_pilot_eu_west_4
from resources.utils import encode_tls_secret_data

OPTS = pulumi.ResourceOptions(provider=k8s_provider_auto_pilot_eu_west_4)


n8n_ns = k8s.core.v1.Namespace("n8n_ns", metadata={"name": "n8n"}, opts=OPTS)

n8n_tls_secret = k8s.core.v1.Secret(
    "n8n_tls_secret",
    metadata={"name": "n8n-tls-secret", "namespace": n8n_ns.metadata["name"]},
    data=Output.all(
        n8n_origin_ca_cert_bundle[0].certificate,
        n8n_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = Path(__file__).parent / "values" / "n8n.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    def prepare_values(
        host, port, user, password, database, domain, tls_secret_name, encryption_key
    ):
        return {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "domain": domain,
            "tls_secret_name": tls_secret_name,
            "encryption_key": encryption_key,
        }

    values = Output.all(
        psql_par_1_instance.load_balancers[0].ip,
        psql_par_1_instance.load_balancers[0].port,
        n8n_dolphin_user.name,
        n8n_dolphin_user.password,
        n8n_dolphin_db.name,
        n8n_tqtensor_com.hostname,
        n8n_tls_secret.metadata["name"],
        random.RandomPassword("n8n_encryption_key", special=False, length=32).result,
    ).apply(
        lambda args: prepare_values(
            args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7]
        )
    )

    chart_values["config"]["database"]["postgresdb"]["host"] = values["host"]
    chart_values["config"]["database"]["postgresdb"]["port"] = values["port"]
    chart_values["config"]["database"]["postgresdb"]["user"] = values["user"]
    chart_values["config"]["database"]["postgresdb"]["database"] = values["database"]
    chart_values["secret"]["database"]["postgresdb"]["password"] = values["password"]

    chart_values["ingress"]["hosts"][0]["host"] = values["domain"]
    chart_values["ingress"]["tls"][0]["hosts"][0] = values["domain"]
    chart_values["ingress"]["tls"][0]["secretName"] = values["tls_secret_name"]

    chart_values["extraEnv"]["WEBHOOK_URL"] = values["domain"]
    chart_values["extraEnv"]["ENCRYPTION_KEY"] = values["encryption_key"]

chart_file_path = str(Path(__file__).parent / "charts" / "n8n-0.25.2.tgz")
n8n_release = k8s.helm.v3.Release(
    "n8n",
    k8s.helm.v3.ReleaseArgs(
        chart=chart_file_path,
        name="n8n",
        namespace=n8n_ns.metadata["name"],
        values=chart_values,
        version="0.25.2",
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_auto_pilot_eu_west_4,
        depends_on=[n8n_ns, n8n_tls_secret],
    ),
)
