import pulumi_awsx as awsx

from resources.utils import get_options

OPTS = get_options(profile="pixelml", region="eu-central-1", type="resource")


pixelml_eu_central_1_vpc = awsx.ec2.Vpc(
    "pixelml_eu_central_1_vpc",
    cidr_block="172.16.0.0/16",
    enable_dns_hostnames=True,
    nat_gateways=awsx.ec2.NatGatewayConfigurationArgs(
        strategy=awsx.ec2.NatGatewayStrategy.SINGLE,
    ),
    subnet_specs=[
        awsx.ec2.SubnetSpecArgs(
            type=awsx.ec2.SubnetType.PUBLIC,
            cidr_mask=20,
        ),
        awsx.ec2.SubnetSpecArgs(
            type=awsx.ec2.SubnetType.PRIVATE,
            cidr_mask=24,
        ),
    ],
    subnet_strategy=awsx.ec2.SubnetAllocationStrategy.AUTO,
    opts=OPTS,
)
