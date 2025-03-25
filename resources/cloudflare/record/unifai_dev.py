import pulumi_cloudflare as cloudflare

from resources.constants import unifai_dev
from resources.utils import get_options
from resources.vm import nginx_ip_eu_west_4

OPTS = get_options(provider="cloudflare")

tei_unifai_dev = cloudflare.Record(
    "tei_unifai_dev",
    name="tei",
    ttl=1,
    type="A",
    content=nginx_ip_eu_west_4.address,
    zone_id=unifai_dev.id,
    proxied=True,
    opts=OPTS,
)
