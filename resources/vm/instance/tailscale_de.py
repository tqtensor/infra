import pulumi
import pulumi_aws as aws

from resources.utils import get_options
from resources.vm.keypair import krypfolio_eu_central_1_key_pair
from resources.vm.networking import krypfolio_eu_central_1_vpc

OPTS = get_options(profile="krypfolio", region="eu-central-1", type="resource")


tailscale_de_sg = aws.ec2.SecurityGroup(
    "tailscale_de_sg",
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
    name="tailscale_de_sg",
    vpc_id=krypfolio_eu_central_1_vpc.vpc_id,
    opts=OPTS,
)

tailscale_de_subnet = aws.ec2.Subnet.get(
    "tailscale_de_subnet",
    id=krypfolio_eu_central_1_vpc.public_subnet_ids[0],
    opts=OPTS,
)

tailscale_de_instance = aws.ec2.Instance(
    "tailscale_de_instance",
    ami="ami-0745b7d4092315796",
    associate_public_ip_address=True,
    availability_zone=tailscale_de_subnet.availability_zone,
    capacity_reservation_specification={
        "capacity_reservation_preference": "open",
    },
    credit_specification={
        "cpu_credits": "standard",
    },
    ebs_optimized=True,
    instance_initiated_shutdown_behavior="stop",
    instance_type=aws.ec2.InstanceType.T3_MICRO,
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
        "volume_size": 40,
        "volume_type": "gp3",
    },
    subnet_id=tailscale_de_subnet.id,
    tags={
        "Name": "tailscale_de-instance",
    },
    tenancy=aws.ec2.Tenancy.DEFAULT,
    vpc_security_group_ids=[tailscale_de_sg.id],
    opts=OPTS,
)

tailscale_de_eip = aws.ec2.Eip(
    "tailscale_de_eip",
    domain="vpc",
    network_border_group=tailscale_de_subnet.availability_zone.apply(
        lambda az: az[:-1]
    ),
    tags={"Name": "tailscale_de-eip"},
    opts=OPTS,
)

tailscale_de_eip_assoc = aws.ec2.EipAssociation(
    "tailscale_de_eip_assoc",
    instance_id=tailscale_de_instance.id,
    private_ip_address=tailscale_de_instance.private_ip,
    public_ip=tailscale_de_eip.public_ip,
    opts=OPTS,
)

pulumi.export("VM: tailscale_de: IP", tailscale_de_eip.public_ip)
