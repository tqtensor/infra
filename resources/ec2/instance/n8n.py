import pulumi
import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(
    profile="krypfolio", region="ap-southeast-1", type="resource", protect=False
)


n8n_vpc = aws.ec2.Vpc(
    "n8n_vpc",
    cidr_block="172.31.0.0/16",
    enable_dns_hostnames=True,
    instance_tenancy="default",
    opts=OPTS,
)

n8n_gw = aws.ec2.InternetGateway(
    "n8n_gw",
    vpc_id=n8n_vpc.id,
    tags={
        "Name": "n8n-gw",
    },
    opts=OPTS,
)

n8n_rt = aws.ec2.RouteTable(
    "n8n_rt",
    routes=[
        {
            "cidr_block": "0.0.0.0/0",
            "gateway_id": n8n_gw.id,
        }
    ],
    vpc_id=n8n_vpc.id,
    opts=OPTS,
)

n8n_subnet = aws.ec2.Subnet(
    "n8n_subnet",
    availability_zone="ap-southeast-1b",
    cidr_block="172.31.16.0/20",
    map_public_ip_on_launch=True,
    private_dns_hostname_type_on_launch="ip-name",
    vpc_id=n8n_vpc.id,
    opts=OPTS,
)

n8n_rt_assoc = aws.ec2.RouteTableAssociation(
    "n8n_rt_assoc",
    route_table_id=n8n_rt.id,
    subnet_id=n8n_subnet.id,
    opts=OPTS,
)

n8n_sg = aws.ec2.SecurityGroup(
    "n8n_sg",
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
    vpc_id=n8n_vpc.id,
    opts=OPTS,
)

n8n_key_pair = aws.ec2.KeyPair(
    "n8n_key_pair",
    key_name="infra",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCwKxF5yPTNedZnbYyS5qxtJThkCnpgp8UtB6NiYSmyfF/vSp7kr1IS5NSOLPizjNd7qY0m6+23Knu6f/hFrTXKePVBtf+6YT5NBc7ptfwiSY95u9awXpfthfjMOVNgM6Tcep0pECd2fx537cWXzlLJfR09oEPivXCDYil1Oqm87cwOjyDCl33pfF/sH7ovKB8jKpvMxtQ59I5ejohx1EmokvhzCyO8guS5utoymz+tCWcCSuUiY1eWFlj09NG5xKbpp9bXXDs4lHQH9JUSuTvDxYtz6shPv2k8C0jk4+IUpzzj0dzaitlQ13jzoFUKBMi7hEzPvanv1GEQHJzm06fGgyALhSta/o5yPWn5gauGhOw7BEC482T3EbwEmIyxqv/+SqKEd+Cx0ieGuridNAhG/G/RuVEkWCSWIIIhv0dIBKDcB3j+dPnHWDHIdJ8537ZoyeS1ZKEPJtrXbSryaVgFV71vO5jQVYStn9HdkHyGCtU9Epsjl5JBhQP2snbE/EraGcpT6EXJc3H9LVd2e0pvfMPh3ujUHIZe7szKibyDKlfAJk6sk3Y2NfooKHrtqyYOjekEXWX36ZBg1lFRgF8l33b4JBZxRmCOMJT/c4H3IzLCYVxXiyQlzgxmpFqSKc4v0ocFsRfLAl9H82Se8qrWTlx0fjSvr+/kfCSIqQjS4Q== tangquocthai@Mac.home\n",
    opts=OPTS,
)

n8n_instance = aws.ec2.Instance(
    "n8n_instance",
    ami="ami-0672fd5b9210aa093",
    associate_public_ip_address=True,
    availability_zone=n8n_subnet.availability_zone,
    capacity_reservation_specification={
        "capacity_reservation_preference": "open",
    },
    credit_specification={
        "cpu_credits": "standard",
    },
    ebs_optimized=True,
    instance_initiated_shutdown_behavior="stop",
    instance_type=aws.ec2.InstanceType.T3_X_LARGE,
    key_name=n8n_key_pair.key_name,
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
    subnet_id=n8n_subnet.id,
    tags={
        "Name": "n8n-instance",
    },
    tenancy=aws.ec2.Tenancy.DEFAULT,
    vpc_security_group_ids=[n8n_sg.id],
    opts=OPTS,
)

n8n_eip = aws.ec2.Eip(
    "n8n_eip",
    domain="vpc",
    network_border_group=n8n_subnet.availability_zone.apply(lambda az: az[:-1]),
    tags={"Name": "n8n-eip"},
    opts=OPTS,
)

n8n_eip_assoc = aws.ec2.EipAssociation(
    "n8n_eip_assoc",
    instance_id=n8n_instance.id,
    private_ip_address=n8n_instance.private_ip,
    public_ip=n8n_eip.public_ip,
    opts=OPTS,
)

pulumi.export("n8n: EIP", n8n_eip.public_ip)
