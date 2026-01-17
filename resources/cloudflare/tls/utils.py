from typing import Tuple

import pulumi_cloudflare as cloudflare
import pulumi_tls as tls
from pulumi_cloudflare import DnsRecord


def create_origin_ca_cert(
    host: DnsRecord,
    zone_name: str = "tqtensor.com",
) -> Tuple[cloudflare.OriginCaCertificate, tls.PrivateKey]:
    def make_resources(
        hostname: str,
    ) -> Tuple[cloudflare.OriginCaCertificate, tls.PrivateKey]:
        # Construct FQDN from subdomain + zone
        fqdn = f"{hostname}.{zone_name}"

        private_key = tls.PrivateKey(
            f"{hostname}_private_key", algorithm="RSA", rsa_bits=2048
        )
        csr = tls.CertRequest(
            f"{hostname}_csr",
            private_key_pem=private_key.private_key_pem,
            subject=tls.CertRequestSubjectArgs(
                common_name=fqdn,
            ),
        )
        origin_ca_cert = cloudflare.OriginCaCertificate(
            f"{hostname}_origin_ca_cert",
            csr=csr.cert_request_pem,
            hostnames=[fqdn],
            request_type="origin-rsa",
            requested_validity=365,  # 1 year
        )
        return origin_ca_cert, private_key

    return host.name.apply(make_resources)
