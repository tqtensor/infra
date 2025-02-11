import os

import pulumi
import pulumi_postgresql as postgresql
from sopsy import Sops

from resources.db.rds import (
    krypfolio_eu_central_1_rds_cluster_instance,
    krypfolio_eu_central_1_rds_credentials,
)

postgres_provider = postgresql.Provider(
    "postgres_provider",
    host=krypfolio_eu_central_1_rds_cluster_instance.endpoint,
    port=5432,
    username=krypfolio_eu_central_1_rds_credentials["username"],
    password=krypfolio_eu_central_1_rds_credentials["password"],
    superuser=False,
)

opts = pulumi.ResourceOptions(provider=postgres_provider)

credentials_file_path = os.path.join(os.path.dirname(__file__), "credentials.yaml")
sops = Sops(credentials_file_path)
try:
    credentials = sops.decrypt()
except Exception as e:
    pulumi.log.error(f"Failed to decrypt {credentials_file_path}: {e}")
    raise


def create_db_and_user(username: str, credentials: dict):
    db = postgresql.Database(
        f"n8n_{username}db",
        name=f"n8n_{username}_db",
        opts=opts,
    )

    role = postgresql.Role(
        f"n8n_{username}_user",
        name=credentials["dolphin"]["username"],
        password=credentials["dolphin"]["password"],
        login=True,
        opts=opts,
    )

    grant_privileges = postgresql.Grant(
        f"n8n_{username}_grant_privileges",
        database=db.name,
        role=role.name,
        object_type="database",
        privileges=["CREATE", "CONNECT"],
        opts=opts,
    )
    return db, role, grant_privileges


n8n_dolphin_db, n8n_dolphin_user, n8n_dolphin_grant_privileges = create_db_and_user(
    username="dolphin", credentials=credentials
)
