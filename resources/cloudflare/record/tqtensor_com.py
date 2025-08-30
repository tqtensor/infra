import pulumi_cloudflare as cloudflare

from resources.constants import nginx_ip_par_2, tqtensor_com
from resources.utils import get_options

OPTS = get_options(provider="cloudflare")


airbyte_tqtensor_com = cloudflare.Record(
    "airbyte_tqtensor_com",
    name="airbyte",
    ttl=1,
    type="A",
    content=nginx_ip_par_2.ip_address,
    zone_id=tqtensor_com.id,
    proxied=True,
    opts=OPTS,
)

mlflow_tqtensor_com = cloudflare.Record(
    "mlflow_tqtensor_com",
    name="mlflow",
    ttl=1,
    type="A",
    content=nginx_ip_par_2.ip_address,
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
