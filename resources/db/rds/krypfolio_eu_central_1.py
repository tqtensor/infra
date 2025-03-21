import json

import pulumi
import pulumi_aws as aws

from resources.utils import get_options
from resources.vm import krypfolio_eu_central_1_vpc

OPTS = get_options(profile="krypfolio", region="eu-central-1", type="resource")


krp_eu_central_1_rds_sg = aws.ec2.SecurityGroup(
    "krp_eu_central_1_rds_sg",
    vpc_id=krypfolio_eu_central_1_vpc.vpc_id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=5432,
            to_port=5432,
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
    opts=OPTS,
)

krp_eu_central_1_rds_subnet_group = aws.rds.SubnetGroup(
    "krp_eu_central_1_rds_subnet_group",
    subnet_ids=krypfolio_eu_central_1_vpc.public_subnet_ids,
    opts=OPTS,
)

krp_eu_central_1_rds_cluster = aws.rds.Cluster(
    "krp_eu_central_1_rds_cluster",
    cluster_identifier="krypfolio-eu-central-1-rds-cluster",
    engine=aws.rds.EngineType.AURORA_POSTGRESQL,
    engine_mode=aws.rds.EngineMode.PROVISIONED,
    engine_version="14.15",
    database_name="postgres",
    master_username="tqtensor",
    manage_master_user_password=True,
    storage_encrypted=True,
    enable_http_endpoint=True,
    serverlessv2_scaling_configuration=aws.rds.ClusterServerlessv2ScalingConfigurationArgs(
        max_capacity=1,
        min_capacity=0,
    ),
    vpc_security_group_ids=[krp_eu_central_1_rds_sg.id],
    db_subnet_group_name=krp_eu_central_1_rds_subnet_group.name,
    skip_final_snapshot=True,
    backup_retention_period=7,
    preferred_backup_window="01:00-02:00",
    preferred_maintenance_window="sun:03:00-sun:04:00",
    copy_tags_to_snapshot=True,
    deletion_protection=True,
    opts=OPTS,
)

krp_eu_central_1_rds_cluster_instance = aws.rds.ClusterInstance(
    "krp_eu_central_1_rds_cluster_instance",
    cluster_identifier=krp_eu_central_1_rds_cluster.id,
    instance_class="db.serverless",
    engine=aws.rds.EngineType.AURORA_POSTGRESQL,
    engine_version="14.15",
    publicly_accessible=True,
    opts=OPTS,
)

krp_eu_central_1_rds_credentials = json.loads(
    aws.secretsmanager.get_secret_version(
        secret_id=krp_eu_central_1_rds_cluster.master_user_secrets.apply(
            lambda x: x[0].secret_arn
        ),
        opts=get_options(profile="krypfolio", region="eu-central-1", type="invoke"),
    ).secret_string
)

pulumi.export("RDS: ARN", krp_eu_central_1_rds_cluster.arn)
pulumi.export("RDS: endpoint", krp_eu_central_1_rds_cluster.endpoint)
