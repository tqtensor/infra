import pulumi_cloudflare as cloudflare

from resources.constants import tqtensor_com
from resources.utils import get_options

OPTS = get_options(provider="cloudflare")


wedding_tqtensor_com = cloudflare.Record(
    "wedding_tqtensor_com",
    name="www.wedding",
    ttl=1,
    type="CNAME",
    content="cname.iwedding.info",
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)
