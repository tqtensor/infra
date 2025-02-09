import base64
from typing import Union

import pulumi

from resources.providers import *  # noqa


def get_options(
    profile: str = "personal",
    region: str = "us-east-1",
    type: str = "resource",
    protect: bool = True,
    provider: str = "aws",
) -> Union[pulumi.ResourceOptions, pulumi.InvokeOptions]:
    if provider in ["aws", "gcp"]:
        if type == "resource":
            return pulumi.ResourceOptions(
                provider=eval(f"{provider}_{profile}_{region.replace('-', '_')}"),
                protect=protect,
            )
        elif type == "invoke":
            return pulumi.InvokeOptions(
                provider=eval(f"{provider}_{profile}_{region.replace('-', '_')}")
            )
        else:
            raise ValueError("Invalid type")
    elif provider == "cloudflare":
        if type == "resource":
            return pulumi.ResourceOptions(
                protect=protect,
            )
        elif type == "invoke":
            return pulumi.InvokeOptions(protect=protect)
    else:
        raise ValueError("Invalid provider")


def encode_tls_secret_data(cert_pem, key_pem):
    return {
        "tls.crt": base64.b64encode(cert_pem.encode()).decode(),
        "tls.key": base64.b64encode(key_pem.encode()).decode(),
    }
