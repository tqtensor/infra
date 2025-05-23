import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import mlflow_tqtensor_com

mlflow_private_key = tls.PrivateKey(
    "mlflow_private_key", algorithm="RSA", rsa_bits=2048
)

mlflow_csr = tls.CertRequest(
    "mlflow_csr",
    private_key_pem=mlflow_private_key.private_key_pem,
    subject=tls.CertRequestSubjectArgs(
        common_name=mlflow_tqtensor_com.hostname,
    ),
)

mlflow_origin_ca_cert = cloudflare.OriginCaCertificate(
    "mlflow_origin_ca_cert",
    csr=mlflow_csr.cert_request_pem,
    hostnames=[mlflow_tqtensor_com.hostname],
    request_type="origin-rsa",
    requested_validity=365,  # 1 year
)
