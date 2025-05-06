import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import vllm_tqtensor_com

vllm_private_key = tls.PrivateKey("vllm_private_key", algorithm="RSA", rsa_bits=2048)

vllm_csr = tls.CertRequest(
    "vllm_csr",
    private_key_pem=vllm_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=vllm_tqtensor_com.hostname,
    ),
)

vllm_origin_ca_cert = cloudflare.OriginCaCertificate(
    "vllm_origin_ca_cert",
    csr=vllm_csr.cert_request_pem,
    hostnames=[vllm_tqtensor_com.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
