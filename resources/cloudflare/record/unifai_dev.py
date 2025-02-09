import pulumi_cloudflare as cloudflare

from resources.constants import unifai_dev
from resources.utils import get_options
from resources.vm import nginx_ip_europe_west_4

OPTS = get_options(provider="cloudflare")


litellm_unifai_dev = cloudflare.Record(
    "litellm_unifai_dev",
    name="litellm",
    ttl=1,
    type="A",
    content=nginx_ip_europe_west_4.address,
    zone_id=unifai_dev.id,
    proxied=True,
    opts=OPTS,
)
