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
        f"{username}_db",
        name=f"{username}_db",
        opts=OPTS,
    )

    role = postgresql.Role(
        f"{username}_user",
        name=username,
        password=credentials[username]["password"],
        login=True,
        create_database=True,
        opts=OPTS,
    )

    grant_privileges = postgresql.Grant(
        f"{username}_grant_privileges",
        database=db.name,
        role=role.name,
        object_type="database",
        privileges=["CREATE", "CONNECT"],
        opts=OPTS,
    )
    return db, role, grant_privileges


airbyte_db, airbyte_user, airbyte_grant_privileges = create_db_and_user(
    username="airbyte"
)
