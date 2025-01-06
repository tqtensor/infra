import pulumi_aws as aws

# Krypfolio AWS account
aws_eu_central_1 = aws.Provider(
    "aws-eu-central-1", region="eu-central-1", profile="krypfolio"
)
aws_us_east_1 = aws.Provider("aws-us-east-1", region="us-east-1", profile="krypfolio")

# Personnal AWS account
aws_personal = aws.Provider("aws-personal", region="us-east-1", profile="personal")
