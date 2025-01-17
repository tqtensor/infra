from typing import Union

import pulumi

from resources.providers.aws import *  # noqa


def get_options(
    profile: str = "personal",
    region: str = "us-east-1",
    type: str = "resource",
    protect: bool = True,
) -> Union[pulumi.ResourceOptions, pulumi.InvokeOptions]:
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
