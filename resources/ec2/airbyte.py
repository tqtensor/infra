import pulumi
import pulumi_aws as aws

from resources.providers.aws import aws_us_east_1

OPTS = pulumi.ResourceOptions(
    protect=True,
    provider=aws_us_east_1,
)


def create_airbyte_instance():
    airbyte_vpc = aws.ec2.Vpc(
        "airbyte_vpc",
        cidr_block="172.31.0.0/16",
        enable_dns_hostnames=True,
        instance_tenancy="default",
        opts=OPTS,
    )

    airbyte_gw = aws.ec2.InternetGateway(
        "airbyte_gw",
        vpc_id=airbyte_vpc.id,
        tags={
            "Name": "airbyte-gw",
        },
        opts=OPTS,
    )

    airbyte_rt = aws.ec2.RouteTable(
        "airbyte_rt",
        routes=[
            {
                "cidr_block": "0.0.0.0/0",
                "gateway_id": airbyte_gw.id,
            }
        ],
        vpc_id=airbyte_vpc.id,
        opts=OPTS,
    )

    airbyte_subnet_a = aws.ec2.Subnet(
        "airbyte_subnet_a",
        availability_zone="us-east-1a",
        cidr_block="172.31.32.0/20",
        map_public_ip_on_launch=True,
        private_dns_hostname_type_on_launch="ip-name",
        vpc_id=airbyte_vpc.id,
        opts=OPTS,
    )

    airbyte_subnet_b = aws.ec2.Subnet(
        "airbyte_subnet_b",
        availability_zone="us-east-1b",
        cidr_block="172.31.16.0/20",
        map_public_ip_on_launch=True,
        private_dns_hostname_type_on_launch="ip-name",
        vpc_id=airbyte_vpc.id,
        opts=OPTS,
    )

    airbyte_rt_assoc_a = aws.ec2.RouteTableAssociation(
        "airbyte_rt_assoc_a",
        route_table_id=airbyte_rt.id,
        subnet_id=airbyte_subnet_a.id,
        opts=OPTS,
    )

    airbyte_rt_assoc_b = aws.ec2.RouteTableAssociation(
        "airbyte_rt_assoc_b",
        route_table_id=airbyte_rt.id,
        subnet_id=airbyte_subnet_b.id,
        opts=OPTS,
    )

    airbyte_sg = aws.ec2.SecurityGroup(
        "airbyte_sg",
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
            {
                "cidr_blocks": ["0.0.0.0/0"],
                "from_port": 8080,
                "protocol": "tcp",
                "to_port": 8080,
            },
        ],
        name="airbyte-sg",
        vpc_id=airbyte_vpc.id,
        opts=OPTS,
    )

    airbyte_key_pair = aws.ec2.KeyPair(
        "airbyte_key_pair",
        key_name="infra",
        public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n",
        opts=OPTS,
    )

    airbyte_instance = aws.ec2.Instance(
        "airbyte_instance",
        ami="ami-0e2c8caa4b6378d8c",
        associate_public_ip_address=True,
        availability_zone=airbyte_subnet_b.availability_zone,
        capacity_reservation_specification={
            "capacity_reservation_preference": "open",
        },
        credit_specification={
            "cpu_credits": "standard",
        },
        ebs_optimized=True,
        instance_initiated_shutdown_behavior="stop",
        instance_type=aws.ec2.InstanceType.T3A_X_LARGE,
        key_name=airbyte_key_pair.key_name,
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
            "volume_size": 100,
            "volume_type": "gp3",
        },
        subnet_id=airbyte_subnet_b.id,
        tags={
            "Name": "airbyte-instance",
        },
        tenancy=aws.ec2.Tenancy.DEFAULT,
        vpc_security_group_ids=[airbyte_sg.id],
        opts=OPTS,
    )

    airbyte_eip_assoc = aws.ec2.EipAssociation(
        "airbyte_eip_assoc",
        instance_id=airbyte_instance.id,
        private_ip_address=airbyte_instance.private_ip,
        public_ip="3.220.5.254",
        opts=OPTS,
    )
