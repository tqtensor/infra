import base64

import pulumi
import pulumi_gcp as gcp

from resources.utils import get_options

OPTS = get_options(
    profile="personal",
    region="asia-southeast-1",
    type="resource",
    provider="gcp",
    protect=False,
)


gdrive_sa = gcp.serviceaccount.Account(
    "gdrive_sa",
    account_id="gdrive-sa-asia-southeast-1",
    opts=OPTS,
)

gdrive_sa_key = gcp.serviceaccount.Key(
    "gdrive_sa_key",
    service_account_id=gdrive_sa.name,
    public_key_type="TYPE_X509_PEM_FILE",
    opts=OPTS,
)

decoded_private_key = gdrive_sa_key.private_key.apply(
    lambda key: base64.b64decode(key).decode("utf-8")
)

pulumi.export("GDrive: SA", pulumi.Output.secret(decoded_private_key))
