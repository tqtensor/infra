import pulumi
import pulumi_aws as aws

OPTS = pulumi.ResourceOptions(
    protect=False,
    provider=aws.Provider(
        "aws-eu-central-1", region="eu-central-1", profile="krypfolio"
    ),
)


def create_nextcloud():
    nextcloud_vpc = aws.ec2.Vpc(
        "nextcloud_vpc",
        cidr_block="172.31.0.0/16",
        enable_dns_hostnames=True,
        instance_tenancy="default",
        opts=OPTS,
    )

    nextcloud_gw = aws.ec2.InternetGateway(
        "nextcloud_gw",
        vpc_id=nextcloud_vpc.id,
        tags={
            "Name": "nextcloud_gw",
        },
        opts=OPTS,
    )

    nextcloud_rt = aws.ec2.RouteTable(
        "nextcloud_rt",
        routes=[
            {
                "cidr_block": "0.0.0.0/0",
                "gateway_id": nextcloud_gw.id,
            }
        ],
        vpc_id=nextcloud_vpc.id,
        opts=OPTS,
    )

    nextcloud_subnet = aws.ec2.Subnet(
        "nextcloud_subnet",
        availability_zone="eu-central-1b",
        cidr_block="172.31.16.0/20",
        map_public_ip_on_launch=True,
        private_dns_hostname_type_on_launch="ip-name",
        vpc_id=nextcloud_vpc.id,
        opts=OPTS,
    )

    nextcloud_rt_assoc = aws.ec2.RouteTableAssociation(
        "nextcloud_rt_assoc",
        route_table_id=nextcloud_rt.id,
        subnet_id=nextcloud_subnet.id,
        opts=OPTS,
    )

    nextcloud_sg = aws.ec2.SecurityGroup(
        "nextcloud_sg",
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
        name="nextcloud_sg",
        vpc_id=nextcloud_vpc.id,
        opts=OPTS,
    )

    nextcloud_key_pair = aws.ec2.KeyPair(
        "nextcloud_key_pair",
        key_name="infra",
        public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n",
        opts=OPTS,
    )

    nextcloud_instance = aws.ec2.Instance(
        "nextcloud_instance",
        ami="ami-0745b7d4092315796",
        associate_public_ip_address=True,
        availability_zone=nextcloud_subnet.availability_zone,
        capacity_reservation_specification={
            "capacity_reservation_preference": "open",
        },
        credit_specification={
            "cpu_credits": "standard",
        },
        ebs_optimized=True,
        instance_initiated_shutdown_behavior="stop",
        instance_type=aws.ec2.InstanceType.T3A_MEDIUM,
        key_name=nextcloud_key_pair.key_name,
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
        subnet_id=nextcloud_subnet.id,
        tags={
            "Name": "nextcloud_instance",
        },
        tenancy=aws.ec2.Tenancy.DEFAULT,
        vpc_security_group_ids=[nextcloud_sg.id],
        opts=OPTS,
    )

    nextcloud_eip_assoc = aws.ec2.EipAssociation(
        "nextcloud_eip_assoc",
        instance_id=nextcloud_instance.id,
        private_ip_address=nextcloud_instance.private_ip,
        public_ip="3.75.72.239",
        opts=OPTS,
    )
