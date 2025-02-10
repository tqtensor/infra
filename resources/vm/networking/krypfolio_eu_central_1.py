import pulumi_awsx as awsx

from resources.utils import get_options

OPTS = get_options(
    profile="krypfolio", region="eu-central-1", type="resource", protect=False
)


krypfolio_eu_central_1_vpc = awsx.ec2.Vpc(
    "krypfolio_eu_central_1_vpc",
    cidr_block="172.31.0.0/16",
    enable_dns_hostnames=True,
    availability_zone_names=["eu-central-1b"],
    nat_gateways=awsx.ec2.NatGatewayConfigurationArgs(
        strategy=awsx.ec2.NatGatewayStrategy.NONE,
    ),
    subnet_specs=[
        awsx.ec2.SubnetSpecArgs(
            type=awsx.ec2.SubnetType.PUBLIC,
            cidr_mask=20,
        )
    ],
    subnet_strategy=awsx.ec2.SubnetAllocationStrategy.AUTO,
    opts=OPTS,
)
