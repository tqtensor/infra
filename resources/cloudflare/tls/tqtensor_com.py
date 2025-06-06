from resources.cloudflare.record import (
    airbyte_tqtensor_com,
    jupyterhub_tqtensor_com,
    litellm_tqtensor_com,
    mlflow_tqtensor_com,
    n8n_tqtensor_com,
    ragflow_tqtensor_com,
    vllm_tqtensor_com,
)

from .utils import create_origin_ca_cert

airbyte_origin_ca_cert_bundle = create_origin_ca_cert(host=airbyte_tqtensor_com)

jupyterhub_origin_ca_cert_bundle = create_origin_ca_cert(host=jupyterhub_tqtensor_com)

litellm_origin_ca_cert_bundle = create_origin_ca_cert(host=litellm_tqtensor_com)

mlflow_origin_ca_cert_bundle = create_origin_ca_cert(host=mlflow_tqtensor_com)

n8n_origin_ca_cert_bundle = create_origin_ca_cert(host=n8n_tqtensor_com)

ragflow_origin_ca_cert_bundle = create_origin_ca_cert(host=ragflow_tqtensor_com)

vllm_origin_ca_cert_bundle = create_origin_ca_cert(host=vllm_tqtensor_com)
