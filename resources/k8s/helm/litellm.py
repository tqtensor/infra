import base64
from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.api import openai_account_details, openai_keys
from resources.cloudflare.tls import litellm_origin_ca_cert_bundle
from resources.db.instance import psql_par_1_instance
from resources.db.psql import litellm_db, litellm_user
from resources.iam.user import bedrock_access_key, vertex_sa_key, vertex_sa_key_2nd
from resources.k8s.providers import k8s_provider_par_2
from resources.utils import encode_tls_secret_data, fill_in_password

OPTS = pulumi.ResourceOptions(provider=k8s_provider_par_2)


litellm_ns = k8s.core.v1.Namespace(
    "litellm_ns", metadata={"name": "litellm"}, opts=OPTS
)

litellm_env_secret = k8s.core.v1.Secret(
    "litellm_env_secret",
    metadata={"name": "litellm-env-secret", "namespace": litellm_ns.metadata["name"]},
    data=Output.all(
        bedrock_access_key.id,
        bedrock_access_key.secret,
        openai_account_details.properties.endpoint,
        openai_keys,
        vertex_sa_key.private_key,
        vertex_sa_key_2nd.private_key,
    ).apply(
        lambda args: {
            "BEDROCK_AWS_ACCESS_KEY_ID": base64.b64encode(args[0].encode()).decode(),
            "BEDROCK_AWS_SECRET_ACCESS_KEY": base64.b64encode(
                args[1].encode()
            ).decode(),
            "AZURE_API_BASE": base64.b64encode(args[2].encode()).decode(),
            "AZURE_API_KEY": base64.b64encode(args[3].key1.encode()).decode(),
            "VERTEX_SA_KEY": args[4],
            "VERTEX_SA_2ND_KEY": args[5],
        }
    ),
    opts=OPTS,
)

litellm_postgres_secret = k8s.core.v1.Secret(
    "litellm_postgres_secret",
    metadata={
        "name": "litellm-postgres-secret",
        "namespace": litellm_ns.metadata["name"],
    },
    data=Output.all(
        litellm_user.name,
        litellm_user.password,
    ).apply(
        lambda args: {
            "username": base64.b64encode(args[0].encode()).decode(),
            "password": base64.b64encode(args[1].encode()).decode(),
        }
    ),
    opts=OPTS,
)

litellm_tls_secret = k8s.core.v1.Secret(
    "litellm_tls_secret",
    metadata={"name": "litellm-tls-secret", "namespace": litellm_ns.metadata["name"]},
    data=Output.all(
        litellm_origin_ca_cert_bundle[0].certificate,
        litellm_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

secrets_file_path = Path(__file__).parent / "secrets" / "litellm.yaml"
secret_values = fill_in_password(
    encrypted_yaml=secrets_file_path, value_path="masterkey"
)

values_file_path = Path(__file__).parent / "values" / "litellm.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    def prepare_values(host, port):
        return {
            "endpoint": host + ":" + str(port),
        }

    values = Output.all(
        psql_par_1_instance.load_balancers[0].ip,
        psql_par_1_instance.load_balancers[0].port,
    ).apply(lambda args: prepare_values(args[0], args[1]))

    chart_values["masterkey"] = secret_values["masterkey"]
    chart_values["db"]["endpoint"] = values["endpoint"]
    chart_values["db"]["database"] = litellm_db.name

chart_file_path = str(Path(__file__).parent / "charts" / "litellm-helm-0.4.3.tgz")
litellm_release = k8s.helm.v3.Release(
    "litellm-proxy",
    k8s.helm.v3.ReleaseArgs(
        chart=chart_file_path,
        name="litellm-proxy",
        namespace=litellm_ns.metadata["name"],
        values=chart_values,
        version="0.4.3",
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_par_2,
        depends_on=[litellm_ns],
    ),
)
