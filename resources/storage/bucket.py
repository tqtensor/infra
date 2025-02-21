import pulumi_aws as aws

from resources.utils import get_options

EC1_OPTS = get_options(profile="personal", region="eu-central-1", type="resource")
UE1_OPTS = get_options(profile="personal", region="us-east-1", type="resource")


arq_bucket = aws.s3.Bucket(
    "arq_bucket",
    bucket="tqtensor-arq-bucket-eu",
    acl="private",
    opts=EC1_OPTS,
)

n8n_bucket = aws.s3.Bucket(
    "n8n_bucket",
    bucket="tqtensor-n8n-bucket-eu",
    acl="private",
    opts=EC1_OPTS,
)

pulumi_bucket = aws.s3.Bucket(
    "pulumi_bucket",
    bucket="tqtensor-pulumi-bucket-us",
    acl="private",
    opts=UE1_OPTS,
)
