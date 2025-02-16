import pulumi
import pulumi_aws as aws

from resources.utils import get_options
from resources.vm.networking import krypfolio_ap_southeast_1_vpc

OPTS = get_options(profile="krypfolio", region="ap-southeast-1", type="resource")


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
        {
            "cidr_blocks": ["0.0.0.0/0"],
            "from_port": 5000,
            "protocol": "tcp",
            "to_port": 6000,
        },
    ],
    name="n8n_sg",
    vpc_id=krypfolio_ap_southeast_1_vpc.vpc_id,
    opts=OPTS,
)

n8n_subnet = aws.ec2.Subnet.get(
    "n8n_subnet",
    id=krypfolio_ap_southeast_1_vpc.public_subnet_ids[0],
    opts=OPTS,
)

n8n_key_pair = aws.ec2.KeyPair(
    "n8n_key_pair",
    key_name="n8n-key-pair",
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

pulumi.export("n8n: IP", n8n_eip.public_ip)
