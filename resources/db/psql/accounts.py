import pulumi

from resources.db.psql.providers import par_1_postgres_provider
from resources.db.psql.utils import create_db_and_user

OPTS = pulumi.ResourceOptions(provider=par_1_postgres_provider, protect=False)


# Airbyte
airbyte_db, airbyte_user, airbyte_grant_privileges = create_db_and_user(
    username="airbyte", opts=OPTS
)

# MLflow
mlflow_db, mlflow_user, mlflow_grant_privileges = create_db_and_user(
    username="mlflow", opts=OPTS
)
mlflow_auth_db, mlflow_auth_user, mlflow_auth_grant_privileges = create_db_and_user(
    username="mlflow_auth",
    opts=OPTS,
)
