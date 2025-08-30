from resources.cloudflare.record import (
    airbyte_tqtensor_com,
    mlflow_tqtensor_com,
)

from .utils import create_origin_ca_cert

airbyte_origin_ca_cert_bundle = create_origin_ca_cert(host=airbyte_tqtensor_com)

mlflow_origin_ca_cert_bundle = create_origin_ca_cert(host=mlflow_tqtensor_com)
