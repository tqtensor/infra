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
    if provider == "aws":
        if type == "resource":
            return pulumi.ResourceOptions(
                provider=eval(f"aws_{profile}_{region.replace('-', '_')}"),
                protect=protect,
            )
        elif type == "invoke":
            return pulumi.InvokeOptions(
                provider=eval(f"aws_{profile}_{region.replace('-', '_')}")
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
