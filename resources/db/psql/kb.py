import json
import os

import pg8000.native
import pulumi
import pulumi_aws as aws
import pulumi_postgresql as postgresql
from pulumi import Output

from resources.db.psql.providers import krp_ec1_postgres_provider
from resources.db.rds import krp_eu_central_1_rds_cluster_instance
from resources.utils import fill_in_password, get_options

EC1_OPTS = get_options(profile="krypfolio", region="eu-central-1", type="resource")
PSQL_OPTS = pulumi.ResourceOptions(provider=krp_ec1_postgres_provider)


bedrock_db = postgresql.Database("bedrock_db", name="bedrock_db", opts=PSQL_OPTS)

vector_extension = postgresql.Extension(
    "vector_extension", database=bedrock_db.name, name="vector", opts=PSQL_OPTS
)

credentials_file_path = os.path.join(os.path.dirname(__file__), "credentials.yaml")
credentials = fill_in_password(
    encrypted_yaml=credentials_file_path, value_path="roles.bedrock_user.password"
)["roles"]
bedrock_role = postgresql.Role(
    "bedrock_role",
    name="bedrock_user",
    login=True,
    password=credentials["bedrock_user"]["password"],
    opts=PSQL_OPTS,
)

bedrock_db_grant = postgresql.Grant(
    "bedrock_db_grant",
    database=bedrock_db.name,
    role=bedrock_role.name,
    object_type="database",
    privileges=["ALL"],
    opts=PSQL_OPTS,
)

bedrock_schema_grant = postgresql.Grant(
    "bedrock_schema_grant",
    schema="public",
    database=bedrock_db.name,
    role=bedrock_role.name,
    object_type="schema",
    privileges=["ALL"],
    opts=PSQL_OPTS,
)


def create_table(host: str, user: str, password: str, database: str, table: str):
    with pg8000.native.Connection(
        host=host,
        port=5432,
        user=user,
        password=password,
        database=database,
    ) as conn:
        conn.run(
            f"""
        CREATE TABLE IF NOT EXISTS {table} (
            id uuid PRIMARY KEY,
            embedding vector(1536),
            chunks text,
            metadata json
        );"""
        )

        conn.run(
            f"""
        CREATE INDEX IF NOT EXISTS {table}_embedding_idx ON {table}
        USING hnsw (embedding vector_cosine_ops)
        WITH (ef_construction = 256);"""
        )


bedrock_tbl = Output.all(
    krp_eu_central_1_rds_cluster_instance.endpoint,
    bedrock_role.name,
    bedrock_role.password,
    bedrock_db.name,
    "bedrock_tbl",
).apply(
    lambda args: create_table(
        host=args[0],
        user=args[1],
        password=args[2],
        database=args[3],
        table=args[4],
    )
)

bedrock_secret = aws.secretsmanager.Secret(
    "bedrock-db-credentials",
    opts=EC1_OPTS,
)
bedrock_secret_version = aws.secretsmanager.SecretVersion(
    "bedrock_secret_version",
    secret_id=bedrock_secret.id,
    secret_string=Output.all(bedrock_role.name, bedrock_role.password).apply(
        lambda args: json.dumps(
            {
                "username": args[0],
                "password": args[1],
            }
        )
    ),
    opts=EC1_OPTS,
)
