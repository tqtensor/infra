import pulumi_aws as aws

# Krypfolio AWS account
aws_krypfolio_eu_central_1 = aws.Provider(
    "aws-krypfolio-eu-central-1", region="eu-central-1", profile="krypfolio"
)
aws_krypfolio_eu_north_1 = aws.Provider(
    "aws-krypfolio-eu-north-1", region="eu-north-1", profile="krypfolio"
)
aws_krypfolio_us_east_1 = aws.Provider(
    "aws-krypfolio-us-east-1", region="us-east-1", profile="krypfolio"
)
aws_krypfolio_ap_southeast_1 = aws.Provider(
    "aws-krypfolio-ap-southeast-1", region="ap-southeast-1", profile="krypfolio"
)

# Personal AWS account
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
