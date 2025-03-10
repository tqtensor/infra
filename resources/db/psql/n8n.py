import os

import pulumi
import pulumi_postgresql as postgresql

from resources.db.psql.providers import krp_ec1_postgres_provider
from resources.utils import fill_in_password

OPTS = pulumi.ResourceOptions(provider=krp_ec1_postgres_provider)


def create_db_and_user(username: str):
    credentials_file_path = os.path.join(os.path.dirname(__file__), "credentials.yaml")
    credentials = fill_in_password(
        encrypted_yaml=credentials_file_path, value_path=f"roles.{username}.password"
    )["roles"]

    db = postgresql.Database(
        f"n8n_{username}_db",
        name=f"n8n_{username}_db",
        opts=OPTS,
    )

    role = postgresql.Role(
        f"n8n_{username}_user",
        name=f"n8n_{username}_user",
        password=credentials[username]["password"],
        login=True,
        opts=OPTS,
    )

    grant_privileges = postgresql.Grant(
        f"n8n_{username}_grant_privileges",
        database=db.name,
        role=role.name,
        object_type="database",
        privileges=["CREATE", "CONNECT"],
        opts=OPTS,
    )
    return db, role, grant_privileges


n8n_dolphin_db, n8n_dolphin_user, n8n_dolphin_grant_privileges = create_db_and_user(
    username="dolphin"
)

n8n_grokking_db, n8n_grokking_user, n8n_grokking_grant_privileges = create_db_and_user(
    username="grokking"
)

n8n_whale_db, n8n_whale_user, n8n_whale_grant_privileges = create_db_and_user(
    username="whale"
)
