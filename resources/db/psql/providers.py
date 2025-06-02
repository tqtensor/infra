import pulumi_postgresql as postgresql

from resources.db.instance import (
    krp_eu_central_1_rds_cluster_instance,
    krp_eu_central_1_rds_credentials,
    psql_par_1_instance,
)

krp_ec1_postgres_provider = postgresql.Provider(
    "krp_ec1_postgres_provider",
    host=krp_eu_central_1_rds_cluster_instance.endpoint,
    port=5432,
    username=krp_eu_central_1_rds_credentials["username"],
    password=krp_eu_central_1_rds_credentials["password"],
    superuser=False,
)

par_1_postgres_provider = postgresql.Provider(
    "par_1_postgres_provider",
    host=psql_par_1_instance.load_balancers[0].ip,
    port=psql_par_1_instance.load_balancers[0].port,
    username=psql_par_1_instance.user_name,
    password=psql_par_1_instance.password,
    superuser=False,
)
