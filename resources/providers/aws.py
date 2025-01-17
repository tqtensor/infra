import pulumi_aws as aws

# Krypfolio AWS account
aws_krypfolio_eu_central_1 = aws.Provider(
    "aws-krypfolio-eu-central-1", region="eu-central-1", profile="krypfolio"
)
aws_krypfolio_us_east_1 = aws.Provider(
    "aws-krypfolio-us-east-1", region="us-east-1", profile="krypfolio"
)

# Personal AWS account
aws_personal_us_east_1 = aws.Provider(
    "aws-personal-us-east-1", region="us-east-1", profile="personal"
)
