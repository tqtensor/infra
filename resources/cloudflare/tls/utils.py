from typing import Tuple

import pulumi_cloudflare as cloudflare
import pulumi_tls as tls
from pulumi import Output
from pulumi_cloudflare.record import Record


def create_origin_ca_cert(
    host: Record,
) -> Tuple[cloudflare.OriginCaCertificate, tls.PrivateKey]:
    def make_resources(hostname: str):
        private_key = tls.PrivateKey(
            f"{hostname}_private_key", algorithm="RSA", rsa_bits=2048
        )
        csr = tls.CertRequest(
            f"{hostname}_csr",
            private_key_pem=private_key.private_key_pem,
            subject=tls.CertRequestSubjectArgs(
                common_name=hostname,
            ),
        )
        origin_ca_cert = cloudflare.OriginCaCertificate(
            f"{hostname}_origin_ca_cert",
            csr=csr.cert_request_pem,
            hostnames=[hostname],
            request_type="origin-rsa",
            requested_validity=365,  # 1 year
        )
        return origin_ca_cert, private_key

    return Output.all(host.hostname).apply(lambda args: make_resources(args[0]))
