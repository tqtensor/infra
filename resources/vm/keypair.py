import pulumi_aws as aws
import pulumi_gcp as gcp

from resources.utils import get_options

krypfolio_ap_southeast_1_key_pair = aws.ec2.KeyPair(
    "krypfolio_ap_southeast_1_key_pair",
    key_name="infra",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n",
    opts=get_options(profile="krypfolio", region="ap-southeast-1", type="resource"),
)

krypfolio_eu_central_1_key_pair = aws.ec2.KeyPair(
    "krypfolio_eu_central_1_key_pair",
    key_name="infra",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n",
    opts=get_options(profile="krypfolio", region="eu-central-1", type="resource"),
)

krypfolio_eu_north_1_key_pair = aws.ec2.KeyPair(
    "krypfolio_eu_north_1_key_pair",
    key_name="infra",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n",
    opts=get_options(profile="krypfolio", region="eu-north-1", type="resource"),
)

pixelml_eu_central_1_key_pair = aws.ec2.KeyPair(
    "pixelml_eu_central_1_key_pair",
    key_name="infra",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n",
    opts=get_options(profile="pixelml", region="eu-central-1", type="resource"),
)

pixelml_us_east_1_key_pair = aws.ec2.KeyPair(
    "pixelml_us_east_1_key_pair",
    key_name="infra",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n",
    opts=get_options(profile="pixelml", region="us-east-1", type="resource"),
)

pixelml_gcp_us_east_1_key_pair = gcp.compute.ProjectMetadata(
    "pixelml_gcp_us_east_1_key_pair",
    metadata={
        "ssh-keys": "gce:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbnm55mNBsS3Ackocgh2jv79s5Ep4MsTxCD8OnG6QXIk6QvCATYHxHnhXmcokwpjMPiSUJdhbfVTZCq05jCDjEgSFAZRJSOopzmCS0nzpWcdlhvnLRGZinH8zTBwK4AX/aPMfb301fICZf0Z7pZFA4rNTjSaDs591aIlZWC9sJIPJvaglHaFSTdxCyFoX0JFVIcHXxiE0PP1i3ECYAePtlERJtVQ0UkpV5B4XaDrE+Nglp3iaXRDUHYJIirqfVkT4WABlFJu0Em7UzGghOCqyeoSqEm01H+txUs8065EUQ+7MZArSMGXlNr7YVWrWY2fppxDNQ2XSyOer5NSz5y05t infra\n"
    },
    opts=get_options(
        profile="pixelml", region="us-east-1", type="resource", provider="gcp"
    ),
)
