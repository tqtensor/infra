import pulumi

from resources.db.psql.providers import krp_ec1_postgres_provider

from .utils import create_db_and_user

OPTS = pulumi.ResourceOptions(provider=krp_ec1_postgres_provider)


litellm_db, litellm_user, litellm_grant_privileges = create_db_and_user(
    username="litellm", opts=OPTS
)
