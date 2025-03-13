import pulumi_cloudflare as cloudflare

from resources.constants import tqtensor_com
from resources.utils import get_options
from resources.vm import nextcloud_instance, nginx_ip_eu_west_4

OPTS = get_options(provider="cloudflare")

airbyte_tqtensor_com = cloudflare.Record(
    "airbyte_tqtensor_com",
    name="airbyte",
    ttl=1,
    type="A",
    content=nginx_ip_eu_west_4.address,
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)

drive_tqtensor_com = cloudflare.Record(
    "drive_tqtensor_com",
    name="drive",
    ttl=1,
    type="A",
    content=nextcloud_instance.public_ip,
    zone_id=tqtensor_com.id,
    opts=OPTS,
)

grokking_tqtensor_com = cloudflare.Record(
    "grokking_tqtensor_com",
    name="grokking",
    ttl=1,
    type="A",
    content=nginx_ip_eu_west_4.address,
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)

jupyterhub_tqtensor_com = cloudflare.Record(
    "jupyterhub_tqtensor_com",
    name="jupyterhub",
    ttl=1,
    type="A",
    content=nginx_ip_eu_west_4.address,
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)

litellm_tqtensor_com = cloudflare.Record(
    "litellm_tqtensor_com",
    name="litellm",
    ttl=1,
    type="A",
    content=nginx_ip_eu_west_4.address,
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)

n8n_tqtensor_com = cloudflare.Record(
    "n8n_tqtensor_com",
    name="n8n",
    ttl=1,
    type="A",
    content=nginx_ip_eu_west_4.address,
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)

nextcloud_tqtensor_com = cloudflare.Record(
    "nextcloud_tqtensor_com",
    name="nextcloud",
    ttl=1,
    type="A",
    content=nginx_ip_eu_west_4.address,
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)

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
