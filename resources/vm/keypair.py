import pulumi
import pulumi_aws as aws

from resources.providers import aws_krypfolio_eu_central_1, aws_pixelml_us_east_1

krypfolio_eu_central_1_key_pair = aws.ec2.KeyPair(
    "krypfolio_eu_central_1_key_pair",
    key_name="infra",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n",
    opts=pulumi.ResourceOptions(
        provider=aws_krypfolio_eu_central_1,
        protect=True,
    ),
)

pixelml_us_east_1_key_pair = aws.ec2.KeyPair(
    "pixelml_us_east_1_key_pair",
    key_name="infra",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n",
    opts=pulumi.ResourceOptions(
        provider=aws_pixelml_us_east_1,
    ),
)
