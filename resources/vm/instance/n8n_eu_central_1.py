import pulumi
import pulumi_aws as aws

from resources.utils import get_options
from resources.vm.keypair import krypfolio_eu_central_1_key_pair
from resources.vm.networking import (
    krypfolio_eu_central_1_subnet,
    krypfolio_eu_central_1_vpc,
)

OPTS = get_options(profile="krypfolio", region="eu-central-1", type="resource")


n8n_eu_central_1_sg = aws.ec2.SecurityGroup(
    "n8n_eu_central_1_sg",
    egress=[
        {
            "cidr_blocks": ["0.0.0.0/0"],
            "from_port": 0,
            "protocol": "-1",
            "to_port": 0,
        }
    ],
    ingress=[
        {
            "cidr_blocks": ["0.0.0.0/0"],
            "from_port": 22,
            "protocol": "tcp",
            "to_port": 22,
        },
        {
            "cidr_blocks": ["0.0.0.0/0"],
            "from_port": 443,
            "protocol": "tcp",
            "to_port": 443,
        },
        {
            "cidr_blocks": ["0.0.0.0/0"],
            "from_port": 80,
            "protocol": "tcp",
            "to_port": 80,
        },
    ],
    name="n8n_sg",
    vpc_id=krypfolio_eu_central_1_vpc.id,
    opts=OPTS,
)

n8n_eu_central_1_instance = aws.ec2.Instance(
    "n8n_eu_central_1_instance",
    ami="ami-0745b7d4092315796",
    associate_public_ip_address=True,
    availability_zone=krypfolio_eu_central_1_subnet.availability_zone,
    capacity_reservation_specification={
        "capacity_reservation_preference": "open",
    },
    credit_specification={
        "cpu_credits": "standard",
    },
    ebs_optimized=True,
    instance_initiated_shutdown_behavior="stop",
    instance_type=aws.ec2.InstanceType.T3A_MEDIUM,
    key_name=krypfolio_eu_central_1_key_pair.key_name,
    maintenance_options={
        "auto_recovery": "default",
    },
    metadata_options={
        "http_endpoint": "enabled",
        "http_protocol_ipv6": "disabled",
        "http_put_response_hop_limit": 2,
        "http_tokens": "required",
        "instance_metadata_tags": "disabled",
    },
    private_dns_name_options={
        "hostname_type": "ip-name",
    },
    root_block_device={
        "iops": 3000,
        "throughput": 125,
        "volume_size": 200,
        "volume_type": "gp3",
    },
    subnet_id=krypfolio_eu_central_1_subnet.id,
    tags={
        "Name": "n8n-instance",
    },
    tenancy=aws.ec2.Tenancy.DEFAULT,
    vpc_security_group_ids=[n8n_eu_central_1_sg.id],
    opts=OPTS,
)

n8n_eu_central_1_eip = aws.ec2.Eip(
    "n8n_eu_central_1_eip",
    domain="vpc",
    network_border_group=krypfolio_eu_central_1_subnet.availability_zone.apply(
        lambda az: az[:-1]
    ),
    tags={"Name": "n8n-eip"},
    opts=OPTS,
)

n8n_eu_central_1_eip_assoc = aws.ec2.EipAssociation(
    "n8n_eu_central_1_eip_assoc",
    instance_id=n8n_eu_central_1_instance.id,
    private_ip_address=n8n_eu_central_1_instance.private_ip,
    public_ip=n8n_eu_central_1_eip.public_ip,
    opts=OPTS,
)

pulumi.export("n8n: eu-central-1: EIP", n8n_eu_central_1_eip.public_ip)
