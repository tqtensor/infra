import pulumi
import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_europe_west_4
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="europe-west-4", type="resource", provider="gcp"
)


sops_key_ring = gcp.kms.KeyRing(
    "sops_key_ring",
    name="sops",
    location="global",
    project=gcp_pixelml_europe_west_4.project,
)

key = gcp.kms.CryptoKey(
    "sops-key", name="sops-key", key_ring=sops_key_ring.id, purpose="ENCRYPT_DECRYPT"
)

pulumi.export("KMS: SOPS: key_id", key.id)
