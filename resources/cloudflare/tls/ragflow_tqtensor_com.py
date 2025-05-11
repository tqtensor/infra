import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import ragflow_tqtensor_com

ragflow_private_key = tls.PrivateKey(
    "ragflow_private_key", algorithm="RSA", rsa_bits=2048
)

ragflow_csr = tls.CertRequest(
    "ragflow_csr",
    private_key_pem=ragflow_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=ragflow_tqtensor_com.hostname,
    ),
)

ragflow_origin_ca_cert = cloudflare.OriginCaCertificate(
    "ragflow_origin_ca_cert",
    csr=ragflow_csr.cert_request_pem,
    hostnames=[ragflow_tqtensor_com.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
