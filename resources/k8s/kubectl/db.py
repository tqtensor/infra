import pulumi
import pulumi_kubernetes as k8s

from resources.db.instance import psql_par_1_instance
from resources.k8s.providers import k8s_provider_auto_pilot_eu_west_4

OPTS = pulumi.ResourceOptions(provider=k8s_provider_auto_pilot_eu_west_4)


db_ns = k8s.core.v1.Namespace("db_ns", metadata={"name": "db"}, opts=OPTS)

scaleway_db_service = k8s.core.v1.Service(
    "scaleway-db-service",
    metadata={"name": "scaleway-db-service", "namespace": db_ns.metadata["name"]},
    spec={
        "ports": [
            {
                "protocol": "TCP",
                "port": psql_par_1_instance.load_balancers[0].port,
                "targetPort": psql_par_1_instance.load_balancers[0].port,
            }
        ]
    },
    opts=OPTS,
)

scaleway_db_endpoints = k8s.core.v1.Endpoints(
    "scaleway-db-endpoints",
    metadata={"name": "scaleway-db-service", "namespace": db_ns.metadata["name"]},
    subsets=[
        {
            "addresses": [{"ip": psql_par_1_instance.load_balancers[0].ip}],
            "ports": [
                {"port": psql_par_1_instance.load_balancers[0].port, "protocol": "TCP"}
            ],
        }
    ],
    opts=OPTS,
)
