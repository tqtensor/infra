import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import nextcloud_tqtensor_com

nextcloud_private_key = tls.PrivateKey(
    "nextcloud_private_key", algorithm="RSA", rsa_bits=2048
)

nextcloud_csr = tls.CertRequest(
    "nextcloud_csr",
    private_key_pem=nextcloud_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=nextcloud_tqtensor_com.hostname,
    ),
)

nextcloud_origin_ca_cert = cloudflare.OriginCaCertificate(
    "nextcloud_origin_ca_cert",
    csr=nextcloud_csr.cert_request_pem,
    hostnames=[nextcloud_tqtensor_com.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
