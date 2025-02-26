import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import airbyte_tqtensor_com

airbyte_private_key = tls.PrivateKey(
    "airbyte_private_key", algorithm="RSA", rsa_bits=2048
)

airbyte_csr = tls.CertRequest(
    "airbyte_csr",
    private_key_pem=airbyte_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=airbyte_tqtensor_com.hostname,
    ),
)

airbyte_origin_ca_cert = cloudflare.OriginCaCertificate(
    "airbyte_origin_ca_cert",
    csr=airbyte_csr.cert_request_pem,
    hostnames=[airbyte_tqtensor_com.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
