import pulumi
import pulumi_aws as aws

from resources.utils import get_options
from resources.vm.keypair import pixelml_eu_central_1_key_pair
from resources.vm.networking import pixelml_eu_central_1_vpc

OPTS = get_options(profile="pixelml", region="eu-central-1", type="resource")


cag_sg = aws.ec2.SecurityGroup(
    "cag_sg",
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
    name="cag_sg",
    vpc_id=pixelml_eu_central_1_vpc.vpc_id,
    opts=OPTS,
)

cag_subnet = aws.ec2.Subnet.get(
    "cag_subnet",
    id=pixelml_eu_central_1_vpc.public_subnet_ids[0],
    opts=OPTS,
)

cag_instance = aws.ec2.Instance(
    "cag_instance",
    ami="ami-0d077046dda05276a",
    associate_public_ip_address=True,
    availability_zone=cag_subnet.availability_zone,
    capacity_reservation_specification={
        "capacity_reservation_preference": "open",
    },
    credit_specification={
        "cpu_credits": "standard",
    },
    ebs_optimized=True,
    instance_initiated_shutdown_behavior="stop",
    instance_type=aws.ec2.InstanceType.G5_X_LARGE,
    key_name=pixelml_eu_central_1_key_pair.key_name,
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
    subnet_id=cag_subnet.id,
    tags={
        "Name": "cag-instance",
    },
    tenancy=aws.ec2.Tenancy.DEFAULT,
    vpc_security_group_ids=[cag_sg.id],
    opts=OPTS,
)

cag_eip = aws.ec2.Eip(
    "cag_eip",
    domain="vpc",
    network_border_group=cag_subnet.availability_zone.apply(lambda az: az[:-1]),
    tags={"Name": "cag-eip"},
    opts=OPTS,
)

cag_eip_assoc = aws.ec2.EipAssociation(
    "cag_eip_assoc",
    instance_id=cag_instance.id,
    private_ip_address=cag_instance.private_ip,
    public_ip=cag_eip.public_ip,
    opts=OPTS,
)

pulumi.export("VM: CAG: IP", cag_eip.public_ip)
