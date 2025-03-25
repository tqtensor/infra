import pulumi_gcp as gcp
from pulumi import Output

from resources.iam.user import huggingface_sa
from resources.utils import get_options

AE1_OPTS = get_options(
    profile="pixelml",
    region="asia-east-1",
    type="resource",
    provider="gcp",
    protect=False,
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

huggingface_bucket = gcp.storage.Bucket(
    "huggingface_bucket",
    name="huggingface-models-bucket",
    location="EU",
    opts=AE1_OPTS,
)

huggingface_bucket_iam_binding = gcp.storage.BucketIAMBinding(
    "huggingface_bucket_iam_binding",
    bucket=huggingface_bucket.name,
    role="roles/storage.admin",
    members=[Output.format("serviceAccount:{0}", huggingface_sa.email)],
    opts=AE1_OPTS,
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
