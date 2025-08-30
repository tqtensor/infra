import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="eu-central-1", type="resource", protect=False
)


gke_key = aws.kms.Key(
    "gke_key",
    deletion_window_in_days=14,
    opts=OPTS,
)

gke_key_alias = aws.kms.Alias(
    "gke_key_alias",
    name="alias/gke-key",
    target_key_id=gke_key.id,
    opts=OPTS,
)
