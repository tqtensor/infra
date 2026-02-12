from resources.cloudflare.record.tqtensor_com import (
    code_tqtensor_com,
    paper_ai_tqtensor_com,
    paper_tqtensor_com,
    smuggler_tqtensor_com,
    torrent_tqtensor_com,
)
from resources.cloudflare.tls.utils import create_origin_ca_cert

code_origin_ca_cert_bundle = create_origin_ca_cert(
    host=code_tqtensor_com,
)

paper_ai_origin_ca_cert_bundle = create_origin_ca_cert(
    host=paper_ai_tqtensor_com,
)

paper_origin_ca_cert_bundle = create_origin_ca_cert(
    host=paper_tqtensor_com,
)

smuggler_origin_ca_cert_bundle = create_origin_ca_cert(
    host=smuggler_tqtensor_com,
)

torrent_origin_ca_cert_bundle = create_origin_ca_cert(
    host=torrent_tqtensor_com,
)
