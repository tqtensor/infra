from pathlib import Path
from typing import Tuple

import pulumi
import pulumi_postgresql as postgresql

from resources.utils import fill_in_password


def create_db_and_user(
    username: str, opts: pulumi.ResourceOptions
) -> Tuple[postgresql.Database, postgresql.Role, postgresql.Grant]:
    accounts_file_path = Path(__file__).parent / "accounts.yaml"
    accounts = fill_in_password(
        encrypted_yaml=accounts_file_path, value_path=f"roles.{username}.password"
    )["roles"]

    db = postgresql.Database(
        f"{username}_db",
        name=f"{username}_db",
        opts=opts,
    )

    role = postgresql.Role(
        f"{username}_user",
        name=username,
        password=accounts[username]["password"],
        login=True,
        create_database=True,
        opts=opts,
    )

    grant_privileges = postgresql.Grant(
        f"{username}_grant_privileges",
        database=db.name,
        role=role.name,
        object_type="database",
        privileges=["CREATE", "CONNECT"],
        opts=opts,
    )
    return db, role, grant_privileges
