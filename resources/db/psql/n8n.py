import pulumi

from resources.db.psql.providers import krp_ec1_postgres_provider

from .utils import create_db_and_user

OPTS = pulumi.ResourceOptions(provider=krp_ec1_postgres_provider)


n8n_dolphin_db, n8n_dolphin_user, n8n_dolphin_grant_privileges = create_db_and_user(
    username="dolphin", opts=OPTS
)

n8n_whale_db, n8n_whale_user, n8n_whale_grant_privileges = create_db_and_user(
    username="whale", opts=OPTS
)
