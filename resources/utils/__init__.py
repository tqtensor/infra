import base64
from pathlib import Path
from typing import Dict, Union

import pulumi
import pulumi_random as random
import yaml
from sopsy import Sops

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


def encode_tls_secret_data(cert_pem: str, key_pem: str) -> Dict[str, str]:
    return {
        "tls.crt": base64.b64encode(cert_pem.encode()).decode(),
        "tls.key": base64.b64encode(key_pem.encode()).decode(),
    }


def fill_in_password(encrypted_yaml: str, value_path: str) -> dict:
    # Set update flag
    is_updated = False

    # Decrypt the encrypted YAML file using sops
    sops = Sops(encrypted_yaml)
    try:
        credentials = sops.decrypt()
    except Exception as e:
        pulumi.log.error(f"Failed to decrypt {encrypted_yaml}: {e}")
        raise

    # Generate a random password
    password = random.RandomPassword(
        "password", length=32, special=True, override_special="!#$%&-_=+[]<>?"
    )

    # Traverse the value path
    current = credentials
    path_parts = value_path.split(".")

    # Navigate to the nested location
    for part in path_parts[:-1]:
        if part not in current:
            raise ValueError(f"Path {value_path} does not exist in the encrypted YAML")
        current = current[part]

    # Set the password at the final location
    if current.get(path_parts[-1]) == "changeme":
        current[path_parts[-1]] = password.result
        is_updated = True

    if not is_updated:
        return credentials

    # Write updated YAML back to file
    yaml_content = yaml.dump(credentials)
    Path(encrypted_yaml).write_text(yaml_content)

    # Re-encrypt the file in place
    sops = Sops(encrypted_yaml, in_place=True)
    sops.encrypt()
    return credentials
