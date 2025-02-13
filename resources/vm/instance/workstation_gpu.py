import pulumi
import pulumi_aws as aws

from resources.utils import get_options
from resources.vm.keypair import pixelml_us_east_1_key_pair
from resources.vm.networking import pixelml_us_east_1_vpc

OPTS = get_options(
    profile="pixelml", region="us-east-1", type="resource", protect=False
)


workstation_gpu_sg = aws.ec2.SecurityGroup(
    "workstation_gpu_sg",
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
    name="workstation_gpu_sg",
    vpc_id=pixelml_us_east_1_vpc.vpc_id,
    opts=OPTS,
)

workstation_gpu_subnet = aws.ec2.Subnet.get(
    "workstation_gpu_subnet",
    id=pixelml_us_east_1_vpc.public_subnet_ids[0],
    opts=OPTS,
)

workstation_gpu_instance = aws.ec2.Instance(
    "workstation_gpu_instance",
    ami="ami-08ea187523fb45736",
    associate_public_ip_address=True,
    availability_zone=workstation_gpu_subnet.availability_zone,
    capacity_reservation_specification={
        "capacity_reservation_preference": "open",
    },
    credit_specification={
        "cpu_credits": "standard",
    },
    ebs_optimized=True,
    instance_initiated_shutdown_behavior="stop",
    instance_type=aws.ec2.InstanceType.G6_X_LARGE,
    key_name=pixelml_us_east_1_key_pair.key_name,
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
    subnet_id=workstation_gpu_subnet.id,
    tags={
        "Name": "workstation-gpu-instance",
    },
    tenancy=aws.ec2.Tenancy.DEFAULT,
    vpc_security_group_ids=[workstation_gpu_sg.id],
    opts=OPTS,
)

workstation_gpu_eip = aws.ec2.Eip(
    "workstation_gpu_eip",
    domain="vpc",
    network_border_group=workstation_gpu_subnet.availability_zone.apply(
        lambda az: az[:-1]
    ),
    tags={"Name": "workstation-gpu-eip"},
    opts=OPTS,
)

workstation_gpu_eip_assoc = aws.ec2.EipAssociation(
    "workstation_gpu_eip_assoc",
    instance_id=workstation_gpu_instance.id,
    private_ip_address=workstation_gpu_instance.private_ip,
    public_ip=workstation_gpu_eip.public_ip,
    opts=OPTS,
)

pulumi.export("WorkstationGPU: IP", workstation_gpu_eip.public_ip)
pulumi.export("WorkstationGPU: ID", workstation_gpu_instance.id)
