from pathlib import Path

import pulumi
import pulumi_postgresql as postgresql

from resources.utils import fill_in_password


def create_db_and_user(username: str, opts: pulumi.ResourceOptions):
    credentials_file_path = Path(__file__).parent / "credentials.yaml"
    credentials = fill_in_password(
        encrypted_yaml=credentials_file_path, value_path=f"roles.{username}.password"
    )["roles"]

    db = postgresql.Database(
        f"{username}_db",
        name=f"{username}_db",
        opts=opts,
    )

    role = postgresql.Role(
        f"{username}_user",
        name=username,
        password=credentials[username]["password"],
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
