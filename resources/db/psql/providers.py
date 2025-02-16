import pulumi_postgresql as postgresql

from resources.db.rds import krp_ec1_rds_cluster_instance, krp_ec1_rds_credentials

krp_ec1_postgres_provider = postgresql.Provider(
    "krp_ec1_postgres_provider",
    host=krp_ec1_rds_cluster_instance.endpoint,
    port=5432,
    username=krp_ec1_rds_credentials["username"],
    password=krp_ec1_rds_credentials["password"],
    superuser=False,
)
