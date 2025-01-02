import pulumi
import pulumi_aws as aws


def create_airbyte():
    airbyte_vpc = aws.ec2.Vpc(
        "airbyte_vpc",
        cidr_block="172.31.0.0/16",
        enable_dns_hostnames=True,
        instance_tenancy="default",
        opts=pulumi.ResourceOptions(protect=True),
    )

    airbyte_igw = aws.ec2.InternetGateway(
        "airbyte_igw",
        vpc_id=airbyte_vpc.id,
        tags={
            "Name": "airbyte_igw",
        },
        opts=pulumi.ResourceOptions(protect=True),
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
        ],
        name="airbyte_sg",
        vpc_id=airbyte_vpc.id,
        opts=pulumi.ResourceOptions(protect=False),
    )

    airbyte_subnet = aws.ec2.Subnet(
        "airbyte_subnet",
        availability_zone="us-east-1a",
        cidr_block="172.31.0.0/20",
        map_public_ip_on_launch=True,
        private_dns_hostname_type_on_launch="ip-name",
        vpc_id=airbyte_vpc.id,
        opts=pulumi.ResourceOptions(protect=True),
    )

    airbyte_key_pair = aws.ec2.KeyPair(
        "airbyte_key_pair",
        key_name="airbyte",
        public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDIa3KXBrCT/5bm4xwejbyPi4UVKNqhXJ6HHSF6v7R4Fnz75rr2PnapQb/vSNDnmpgUm504dW3ibx3NVefpTb1D7g4sr1sio0lYG7bnDtmg4qF5XwGGEcyBFXh0n+Ovpx2ZMdh5lY7RZdDABrmkmfRuloUU8gW2Qy5G9iP1oedjhB9FEmFZRjp3H7yndfC7WY/RnmRUau738Hp/ub8CRBL+M5tsEI+DQoNHGVpf6QlficolSo+tiKww0+DWoxQf98KF/FAAJTe3Pw6f0QFjoPWXygCBpZlc/oiZtjiddINp5u0v+ospAHRbOnBLsaDfLHeOrDqMVBYmyuKuMULOqkjafqDsYuNvfHOx6ZqMCkW/219vQHiZnQ2qid6JjWkCoh9AZ/C8/zuoy0cwTyYKNfnib1DjfGS7K9S4nFefPRUpZFlrnTRs5XUhmDRKHJ946aqZCLH7iejNtdA2ngljkIhOhWAQXtdtB3MUWWrwPJIFxaK28mJCbqHpJyS/3ygixnls9Zm6QSOXs1DEuy9DHGhffaPBos4c49oQZwx9QwTvfHghHgZjipLFmm3mGEhIhHlH35bEVaWUSeTWSPPAloT0WXtBocAxXttGCKrD2tnYQ6avkeTm81yqImA3KsgzRUG0XHurEtVa076zjLfQVFx+qUKEeopbvXgEgMhvGMmdHQ== victortang212@gmail.com",
        opts=pulumi.ResourceOptions(protect=True),
    )

    airbyte_instance = aws.ec2.Instance(
        "airbyte_instance",
        ami="ami-0e2c8caa4b6378d8c",
        associate_public_ip_address=True,
        availability_zone=airbyte_subnet.availability_zone,
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
        subnet_id=airbyte_subnet.id,
        tags={
            "Name": "airbyte_instance",
        },
        tenancy=aws.ec2.Tenancy.DEFAULT,
        vpc_security_group_ids=[airbyte_sg.id],
        opts=pulumi.ResourceOptions(protect=True),
    )

    airbyte_eip_assoc = aws.ec2.EipAssociation(
        "airbyte_eip_assoc",
        instance_id=airbyte_instance.id,
        private_ip_address=airbyte_instance.private_ip,
        public_ip="3.220.5.254",
        opts=pulumi.ResourceOptions(protect=True),
    )
