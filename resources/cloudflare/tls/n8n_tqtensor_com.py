import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import n8n_tqtensor_com

n8n_private_key = tls.PrivateKey("n8n_private_key", algorithm="RSA", rsa_bits=2048)

n8n_csr = tls.CertRequest(
    "n8n_csr",
    private_key_pem=n8n_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=n8n_tqtensor_com.hostname,
    ),
)

n8n_origin_ca_cert = cloudflare.OriginCaCertificate(
    "n8n_origin_ca_cert",
    csr=n8n_csr.cert_request_pem,
    hostnames=[n8n_tqtensor_com.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
