from typing import Union

import pulumi_aws as aws
import pulumi_gcp as gcp

from resources.utils import get_options


# AWS
def create_infra_key_pair(
    profile: str, region: str, provider: str
) -> Union[aws.ec2.KeyPair, gcp.compute.ProjectMetadata]:
    if provider == "aws":
        return aws.ec2.KeyPair(
            f"{profile}_{provider}_{region}_key_pair".replace("-", "_"),
            key_name="infra",
            public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n",
            opts=get_options(
                profile=profile, region=region, type="resource", provider=provider
            ),
        )
    elif provider == "gcp":
        return gcp.compute.ProjectMetadata(
            f"{profile}_{provider}_{region}_key_pair".replace("-", "_"),
            metadata={
                "ssh-keys": "gce:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n"
            },
            opts=get_options(
                profile=profile, region=region, type="resource", provider=provider
            ),
        )
    else:
        raise ValueError("Invalid provider")


# AWS
pixelml_aws_eu_central_1_key_pair = create_infra_key_pair(
    profile="pixelml", region="eu-central-1", provider="aws"
)
pixelml_aws_us_east_1_key_pair = create_infra_key_pair(
    profile="pixelml", region="us-east-1", provider="aws"
)

# GCP
pixelml_gcp_eu_west_4_key_pair = create_infra_key_pair(
    profile="pixelml", region="eu-west-4", provider="gcp"
)
pixelml_gcp_us_east_1_key_pair = create_infra_key_pair(
    profile="pixelml", region="us-east-1", provider="gcp"
)
