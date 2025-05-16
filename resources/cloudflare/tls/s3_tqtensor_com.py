import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import s3_tqtensor_com

s3_private_key = tls.PrivateKey("s3_private_key", algorithm="RSA", rsa_bits=2048)

s3_csr = tls.CertRequest(
    "s3_csr",
    private_key_pem=s3_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=s3_tqtensor_com.hostname,
    ),
)

s3_origin_ca_cert = cloudflare.OriginCaCertificate(
    "s3_origin_ca_cert",
    csr=s3_csr.cert_request_pem,
    hostnames=[s3_tqtensor_com.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
