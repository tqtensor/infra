import pulumi_cloudflare as cloudflare

from resources.constants import tqtensor_com
from resources.ec2 import n8n_eu_central_1_instance, nextcloud_instance
from resources.utils import get_options

OPTS = get_options(provider="cloudflare")


drive_tqtensor_com = cloudflare.Record(
    "drive_tqtensor_com",
    name="drive",
    ttl=1,
    type="A",
    content=nextcloud_instance.public_ip,
    zone_id=tqtensor_com.id,
    opts=OPTS,
)

n8n_tqtensor_com = cloudflare.Record(
    "n8n_tqtensor_com",
    name="n8n",
    ttl=1,
    type="A",
    content=n8n_eu_central_1_instance.public_ip,
    zone_id=tqtensor_com.id,
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
