import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import tei_tqtensor_com

tei_private_key = tls.PrivateKey("tei_private_key", algorithm="RSA", rsa_bits=2048)

tei_csr = tls.CertRequest(
    "tei_csr",
    private_key_pem=tei_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=tei_tqtensor_com.hostname,
    ),
)

tei_origin_ca_cert = cloudflare.OriginCaCertificate(
    "tei_origin_ca_cert",
    csr=tei_csr.cert_request_pem,
    hostnames=[tei_tqtensor_com.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
