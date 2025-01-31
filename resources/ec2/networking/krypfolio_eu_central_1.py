import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(profile="krypfolio", region="eu-central-1", type="resource")


krypfolio_eu_central_1_vpc = aws.ec2.Vpc(
    "krypfolio_eu_central_1_vpc",
    cidr_block="172.31.0.0/16",
    enable_dns_hostnames=True,
    instance_tenancy="default",
    opts=OPTS,
)

krypfolio_eu_central_1_gw = aws.ec2.InternetGateway(
    "krypfolio_eu_central_1_gw",
    vpc_id=krypfolio_eu_central_1_vpc.id,
    tags={
        "Name": "krypfolio_eu_central_1-gw",
    },
    opts=OPTS,
)

krypfolio_eu_central_1_rt = aws.ec2.RouteTable(
    "krypfolio_eu_central_1_rt",
    routes=[
        {
            "cidr_block": "0.0.0.0/0",
            "gateway_id": krypfolio_eu_central_1_gw.id,
        }
    ],
    vpc_id=krypfolio_eu_central_1_vpc.id,
    opts=OPTS,
)

krypfolio_eu_central_1_subnet = aws.ec2.Subnet(
    "krypfolio_eu_central_1_subnet",
    availability_zone="eu-central-1b",
    cidr_block="172.31.16.0/20",
    map_public_ip_on_launch=True,
    private_dns_hostname_type_on_launch="ip-name",
    vpc_id=krypfolio_eu_central_1_vpc.id,
    opts=OPTS,
)

krypfolio_eu_central_1_rt_assoc = aws.ec2.RouteTableAssociation(
    "krypfolio_eu_central_1_rt_assoc",
    route_table_id=krypfolio_eu_central_1_rt.id,
    subnet_id=krypfolio_eu_central_1_subnet.id,
    opts=OPTS,
)
