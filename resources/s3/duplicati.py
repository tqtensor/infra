import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(
    profile="personal", region="eu-central-1", type="resource", protect=False
)

duplicati_bucket = aws.s3.Bucket(
    "duplicati-bucket",
    bucket="tqtensor-duplicati-bucket-eu",
    acl="private",
    opts=OPTS,
)
