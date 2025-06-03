import pulumi_postgresql as postgresql

from resources.db.instance import psql_par_1_instance

par_1_postgres_provider = postgresql.Provider(
    "par_1_postgres_provider",
    host=psql_par_1_instance.load_balancers[0].ip,
    port=psql_par_1_instance.load_balancers[0].port,
    username=psql_par_1_instance.user_name,
    password=psql_par_1_instance.password,
    superuser=False,
)
