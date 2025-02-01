import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(profile="personal", region="eu-central-1", type="resource")


arq_bucket = aws.s3.Bucket(
    "arq_bucket",
    bucket="tqtensor-arq-bucket-eu",
    acl="private",
    opts=OPTS,
)
