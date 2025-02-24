import pulumi_gcp as gcp
from pulumi import Output

from resources.iam import gke_api_role, gke_control_plane_profile, gke_node_pool_profile
from resources.kms import gke_key
from resources.providers import gcp_pixelml_europe_west_1
from resources.utils import get_options
from resources.vm import pixelml_eu_central_1_vpc

OPTS = get_options(
    profile="pixelml",
    region="europe-west-1",
    type="resource",
    provider="gcp",
    protect=False,
)


required_services = [
    "anthos.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "connectgateway.googleapis.com",
    "gkeconnect.googleapis.com",
    "gkemulticloud.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "opsconfigmonitoring.googleapis.com",
]

for service in required_services:
    gcp.projects.Service(
        f"enable-{service}",
        project=gcp_pixelml_europe_west_1.project,
        service=service,
        disable_dependent_services=True,
        opts=OPTS,
    )

versions = gcp.container.get_aws_versions(
    project=gcp_pixelml_europe_west_1.project, location="europe-west1"
)

cluster_name = "federated-eu-west-1-cluster"

federated_eu_west_1_cluster = gcp.container.AwsCluster(
    "federated_eu_west_1_cluster",
    name=cluster_name,
    aws_region="eu-central-1",
    location="europe-west1",
    control_plane=Output.all(
        gke_api_role.arn,
        gke_key.arn,
        gke_control_plane_profile.name,
        pixelml_eu_central_1_vpc.private_subnet_ids,
    ).apply(
        lambda args: {
            "aws_services_authentication": {
                "role_arn": args[0],
            },
            "config_encryption": {
                "kms_key_arn": args[1],
            },
            "database_encryption": {
                "kms_key_arn": args[1],
            },
            "iam_instance_profile": args[2],
            "subnet_ids": args[3],
            "version": versions.valid_versions[0],
            "instance_type": "t3.medium",
            "tags": {
                "google:gkemulticloud:cluster": cluster_name,
            },
        },
    ),
    authorization={
        "admin_users": [
            {
                "username": "victortang212@gmail.com",
            },
        ],
    },
    fleet=Output.all(
        gcp.organizations.get_project(
            project_id=gcp_pixelml_europe_west_1.project
        ).number
    ).apply(lambda args: {"project": args[0]}),
    networking=Output.all(pixelml_eu_central_1_vpc.vpc_id).apply(
        lambda args: {
            "pod_address_cidr_blocks": ["100.96.0.0/11"],
            "service_address_cidr_blocks": ["100.64.0.0/16"],
            "vpc_id": args[0],
        }
    ),
    opts=OPTS,
)

federated_eu_west_1_primary = gcp.container.AwsNodePool(
    "federated_eu_west_1_primary",
    autoscaling={
        "max_node_count": 5,
        "min_node_count": 1,
    },
    cluster=cluster_name,
    name=f"{cluster_name}-primary",
    location="europe-west1",
    config=Output.all(gke_key.arn, gke_node_pool_profile.name).apply(
        lambda args: {
            "config_encryption": {
                "kms_key_arn": args[0],
            },
            "iam_instance_profile": args[1],
            "instance_type": "t3.medium",
            "tags": {
                "google:gkemulticloud:cluster": cluster_name,
            },
            "taints": [
                {
                    "effect": "prefer_no_schedule",
                    "key": "taint-key",
                    "value": "taint-value",
                }
            ],
            "image_type": "ubuntu",
        }
    ),
    max_pods_constraint={
        "max_pods_per_node": 110,
    },
    subnet_id=pixelml_eu_central_1_vpc.private_subnet_ids[0],
    version=versions.valid_versions[0],
    opts=OPTS,
)
