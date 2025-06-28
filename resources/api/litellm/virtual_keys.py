from pathlib import Path
from typing import List

import requests
from pulumi import Output

from resources.utils import decode_password, fill_in_password

LITELLM_BASE_URL = "https://litellm.tqtensor.com"


def create_virtual_key(name: str) -> Output[dict]:
    virtual_key_path = Path(__file__).parent / "virtual_keys.yaml"
    virtual_key = fill_in_password(
        encrypted_yaml=virtual_key_path, value_path=name, prefix="sk"
    )
    return virtual_key


def make_request(
    virtual_keys: List[str], model: List[str] = None, max_budget: float = 100
):
    litellm_key_path = (
        Path(__file__).parent.parent.parent
        / "k8s"  # noqa: W503
        / "helm"  # noqa: W503
        / "secrets"  # noqa: W503
        / "litellm.yaml"  # noqa: W503
    )
    litellm_key_value = decode_password(encrypted_yaml=litellm_key_path)["masterKey"]

    url = f"{LITELLM_BASE_URL}/key/generate"
    headers = {
        "Authorization": "Bearer {}".format(litellm_key_value),
        "Content-Type": "application/json",
    }

    for virtual_key in virtual_keys:
        virtual_key_path = Path(__file__).parent / "virtual_keys.yaml"
        virtual_key_value = decode_password(encrypted_yaml=virtual_key_path)[
            virtual_key
        ]

        if virtual_key_value == "changeme":
            continue

        data = {
            "key_alias": virtual_key,
            "key": virtual_key_value,
            "models": model if model else None,
            "max_budget": max_budget,
            "user_id": "default_user_id",
        }
        requests.post(url, headers=headers, json=data)


cag_key = create_virtual_key(name="cag")
continue_dev_key = create_virtual_key(name="continue_dev")
nextchat_key = create_virtual_key(name="nextchat")
pixelml_key = create_virtual_key(name="pixelml")
ragflow_key = create_virtual_key(name="ragflow")
stx_key = create_virtual_key(name="stx")

make_request(
    virtual_keys=["cag", "continue_dev", "nextchat", "pixelml", "ragflow", "stx"],
    max_budget=100,
)
