import pulumi_aws as aws

# Personal AWS account
aws_personal_ap_southeast_1 = aws.Provider(
    "aws-personal-ap-southeast-1", region="ap-southeast-1", profile="personal"
)
aws_personal_eu_central_1 = aws.Provider(
    "aws-personal-eu-central-1", region="eu-central-1", profile="personal"
)
aws_personal_us_east_1 = aws.Provider(
    "aws-personal-us-east-1", region="us-east-1", profile="personal"
)

# PixelML AWS account
aws_pixelml_eu_central_1 = aws.Provider(
    "aws-pixelml-eu-central-1", region="eu-central-1", profile="pixelml"
)
aws_pixelml_us_east_1 = aws.Provider(
    "aws-pixelml-us-east-1", region="us-east-1", profile="pixelml"
)

# STX AWS account
aws_stx_us_east_1 = aws.Provider("aws-stx-us-east-1", region="us-east-1", profile="stx")
