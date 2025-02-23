import os
from pathlib import Path

import pandas as pd
import pulumi
import pulumi_postgresql as postgresql
import pulumi_random as random

from resources.db.psql.providers import krp_ec1_postgres_provider
from resources.utils import normalize_email

OPTS = pulumi.ResourceOptions(provider=krp_ec1_postgres_provider, protect=False)


def create_db_and_user(username: str):
    password = random.RandomPassword(
        f"password_n8n_{username}_user",
        length=32,
        special=True,
        override_special="!#$%&-_=+[]<>?",
    )

    db = postgresql.Database(
        f"n8n_{username}_db",
        name=f"n8n_{username}_db",
        opts=OPTS,
    )

    role = postgresql.Role(
        f"n8n_{username}_user",
        name=f"n8n_{username}_user",
        password=password,
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
    return db, role, grant_privileges, password


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
(
    n8n_{username}_db,
    n8n_{username}_user,
    n8n_{username}_grant_privileges,
    n8n_{username}_password,
) = create_db_and_user(username=username)
"""
    )
