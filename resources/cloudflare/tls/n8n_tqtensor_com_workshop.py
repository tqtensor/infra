import os
from pathlib import Path

import pandas as pd
import pulumi
import pulumi_cloudflare as cloudflare
import pulumi_tls as tls

from resources.cloudflare import *  # noqa
from resources.utils import normalize_email

OPTS = pulumi.ResourceOptions(protect=False)


def create_tls(username: str, record: cloudflare.Record):
    private_key = tls.PrivateKey(
        f"n8n_{username}_private_key", algorithm="RSA", rsa_bits=2048, opts=OPTS
    )

    csr = tls.CertRequest(
        f"n8n_{username}_csr",
        private_key_pem=private_key.private_key_pem,
        subject=tls.CertRequestSubjectArgs(
            common_name=record.hostname,
        ),
        opts=OPTS,
    )

    origin_ca_cert = cloudflare.OriginCaCertificate(
        f"n8n_{username}_origin_ca_cert",
        csr=csr.cert_request_pem,
        hostnames=[record.hostname],
        request_type="origin-rsa",
        requested_validity=365,  # 1 year
        opts=OPTS,
    )
    return origin_ca_cert, private_key


# AWS Workshop
participants = [
    normalize_email(email=email)
    for email in pd.read_csv(
        os.path.join(
            Path(__file__).parent.parent.parent.parent, "artifacts", "participants.csv"
        )
    )["email"].values
]

for participant in participants:
    username = participant.split("@")[0]
    exec(
        f"""
n8n_{username}_origin_ca_cert, n8n_{username}_private_key = create_tls(
    username=username, record={username}_tqtensor_com
)
"""
    )
