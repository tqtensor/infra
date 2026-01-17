import pulumi_cloudflare as cloudflare

from resources.constants import nginx_ip_par_2, tqtensor_com
from resources.utils import get_options

OPTS = get_options(provider="cloudflare")


torrent_tqtensor_com = cloudflare.DnsRecord(
    "torrent_tqtensor_com",
    name="torrent",
    ttl=1,
    type="A",
    content=nginx_ip_par_2.ip_address,
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)

wedding_tqtensor_com = cloudflare.DnsRecord(
    "wedding_tqtensor_com",
    name="www.wedding",
    ttl=1,
    type="CNAME",
    content="cname.iwedding.info",
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)

paper_tqtensor_com = cloudflare.DnsRecord(
    "paper_tqtensor_com",
    name="paper",
    ttl=1,
    type="A",
    content=nginx_ip_par_2.ip_address,
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)

paper_ai_tqtensor_com = cloudflare.DnsRecord(
    "paper_ai_tqtensor_com",
    name="paper-ai",
    ttl=1,
    type="A",
    content=nginx_ip_par_2.ip_address,
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)
