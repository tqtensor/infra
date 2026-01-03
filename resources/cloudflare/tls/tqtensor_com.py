from resources.cloudflare.record.tqtensor_com import torrent_tqtensor_com
from resources.cloudflare.tls.utils import create_origin_ca_cert

torrent_origin_ca_cert_bundle = create_origin_ca_cert(
    host=torrent_tqtensor_com,
)
