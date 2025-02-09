import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import litellm_unifai_dev

litellm_private_key = tls.PrivateKey(
    "litellm_private_key", algorithm="RSA", rsa_bits=2048
)

litellm_csr = tls.CertRequest(
    "litellm_csr",
    private_key_pem=litellm_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=litellm_unifai_dev.hostname,
    ),
)

litellm_origin_ca_cert = cloudflare.OriginCaCertificate(
    "litellm_origin_ca_cert",
    csr=litellm_csr.cert_request_pem,
    hostnames=[litellm_unifai_dev.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
