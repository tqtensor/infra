import pulumi_gcp as gcp

from resources.utils import get_options

AE1_OPTS = get_options(
    profile="pixelml",
    region="asia-east-1",
    type="resource",
    provider="gcp",
)
UW4_OPTS = get_options(
    profile="personal", region="eu-west-4", type="resource", provider="gcp"
)


archive_bucket = gcp.storage.Bucket(
    "archive_bucket",
    name="tqtensor-archive",
    location="EU",
    autoclass=gcp.storage.BucketAutoclassArgs(
        enabled=True,
    ),
    opts=UW4_OPTS,
)

sharing_bucket = gcp.storage.Bucket(
    "sharing_bucket",
    name="tqtensor-sharing",
    location="EU",
    opts=UW4_OPTS,
)

sharing_bucket_iam_binding = gcp.storage.BucketIAMBinding(
    "sharing_bucket_iam_binding",
    bucket=sharing_bucket.name,
    role="roles/storage.objectViewer",
    members=["allUsers"],
    opts=UW4_OPTS,
)
