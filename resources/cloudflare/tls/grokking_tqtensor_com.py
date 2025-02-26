import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import grokking_tqtensor_com

grokking_private_key = tls.PrivateKey(
    "grokking_private_key", algorithm="RSA", rsa_bits=2048
)

grokking_csr = tls.CertRequest(
    "grokking_csr",
    private_key_pem=grokking_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=grokking_tqtensor_com.hostname,
    ),
)

grokking_origin_ca_cert = cloudflare.OriginCaCertificate(
    "grokking_origin_ca_cert",
    csr=grokking_csr.cert_request_pem,
    hostnames=[grokking_tqtensor_com.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
