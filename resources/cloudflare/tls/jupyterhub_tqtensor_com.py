import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import jupyterhub_tqtensor_com

jupyterhub_private_key = tls.PrivateKey(
    "jupyterhub_private_key", algorithm="RSA", rsa_bits=2048
)

jupyterhub_csr = tls.CertRequest(
    "jupyterhub_csr",
    private_key_pem=jupyterhub_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=jupyterhub_tqtensor_com.hostname,
    ),
)

jupyterhub_origin_ca_cert = cloudflare.OriginCaCertificate(
    "jupyterhub_origin_ca_cert",
    csr=jupyterhub_csr.cert_request_pem,
    hostnames=[jupyterhub_tqtensor_com.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
