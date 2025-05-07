import base64
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Union

import pulumi
import pulumi_gcp as gcp
import pulumi_random as random
import pulumiverse_scaleway as sw
import yaml
from pulumi import Output
from sopsy import Sops
from sopsy.errors import SopsyCommandFailedError

from resources.providers import *  # noqa


def get_options(
    profile: str = "personal",
    region: str = "us-east-1",
    type: str = "resource",
    protect: bool = True,
    provider: str = "aws",
    kwargs: dict = {},
) -> Union[pulumi.ResourceOptions, pulumi.InvokeOptions]:
    if provider in ["aws", "az", "gcp", "sw"]:
        if type == "resource":
            return pulumi.ResourceOptions(
                provider=eval(f"{provider}_{profile}_{region.replace('-', '_')}"),
                protect=protect,
                **kwargs,
            )
        elif type == "invoke":
            return pulumi.InvokeOptions(
                provider=eval(f"{provider}_{profile}_{region.replace('-', '_')}"),
                **kwargs,
            )
        else:
            raise ValueError("Invalid type")
    elif provider == "cloudflare":
        if type == "resource":
            return pulumi.ResourceOptions(protect=protect, **kwargs)
        elif type == "invoke":
            return pulumi.InvokeOptions(protect=protect, **kwargs)
    else:
        raise ValueError("Invalid provider")


def encode_tls_secret_data(cert_pem: str, key_pem: str) -> Dict[str, str]:
    return {
        "tls.crt": base64.b64encode(cert_pem.encode()).decode(),
        "tls.key": base64.b64encode(key_pem.encode()).decode(),
    }


def fill_in_password(encrypted_yaml: str, value_path: str, prefix: str = ""):
    # Set update flag
    is_updated = False

    # Decrypt the encrypted YAML file using sops
    sops_decoder = Sops(encrypted_yaml)
    try:
        credentials = sops_decoder.decrypt()
    except SopsyCommandFailedError:
        credentials = yaml.safe_load(open(encrypted_yaml, "r").read())
    except Exception as e:
        pulumi.log.error(f"Failed to decrypt {encrypted_yaml}: {e}")
        raise

    # Generate a random password
    password = random.RandomPassword(
        "password_{yaml_file_name}_{value_path}".format(
            yaml_file_name=os.path.basename(encrypted_yaml).split(".")[0],
            value_path=value_path.replace(".", "_"),
        ),
        length=32,
        special=False,
    )

    # Get the raw string value from the password Output
    password_value = password.result.apply(lambda x: prefix + "-" + x)

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
        current[path_parts[-1]] = password_value
        pulumi.log.info(f"Updated {value_path} with a new password")
        is_updated = True

    if not is_updated:
        return credentials

    # Wait for the Output to resolve before writing to YAML
    def write_credentials(creds: dict):
        # Re-encrypt the file in place
        credentials_content = yaml.dump(creds)
        Path(encrypted_yaml).write_text(credentials_content)
        sops_encoder = Sops(encrypted_yaml, in_place=True)
        sops_encoder.encrypt()
        return creds

    credentials = Output.all(credentials).apply(lambda args: write_credentials(args[0]))
    return credentials


def normalize_email(email: str):
    username = email.split("@")[0]
    username = re.sub(r"[^a-zA-Z0-9]", "", username)
    return f"{username}@{email.split('@')[1]}".strip().lower()


def create_kubeconfig(
    cluster: Union[gcp.container.Cluster, sw.kubernetes.Cluster],
) -> str:
    if isinstance(cluster, gcp.container.Cluster):
        return Output.all(
            cluster.name,
            cluster.endpoint,
            cluster.master_auth,
            cluster.project,
            cluster.location,
        ).apply(
            lambda args: f"""
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {args[2]['cluster_ca_certificate']}
    server: https://{args[1]}
  name: {args[3]}_{args[4]}_{args[0]}
contexts:
- context:
    cluster: {args[3]}_{args[4]}_{args[0]}
    user: {args[3]}_{args[4]}_{args[0]}
  name: {args[3]}_{args[4]}_{args[0]}
current-context: {args[3]}_{args[4]}_{args[0]}
kind: Config
preferences: {{}}
users:
- name: {args[3]}_{args[4]}_{args[0]}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      installHint: Install gke-gcloud-auth-plugin for use with kubectl by following https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke
      provideClusterInfo: true
"""
        )
    elif isinstance(cluster, sw.kubernetes.Cluster):
        return cluster.kubeconfigs[0].config_file
    else:
        raise ValueError(f"Unsupported cluster type: {type(cluster)}")


def create_docker_config(provider: str, server: str):
    # Ensure .docker directory exists
    docker_dir = Path.home() / ".docker"
    docker_dir.mkdir(exist_ok=True, parents=True)
    docker_config_path = docker_dir / "config.json"

    if provider.lower() == "gcp":
        # For GCP, we'll use the gcloud credential helper
        config = {"credHelpers": {server: "gcloud"}}

        # Create the config file
        with open(docker_config_path, "w") as f:
            json.dump(config, f, indent=2)

        # Verify gcloud auth is set up
        try:
            subprocess.check_call(
                ["gcloud", "auth", "print-access-token"], stdout=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            print(
                "Warning: gcloud doesn't seem to be authenticated. Run 'gcloud auth login' first."
            )
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. Currently only 'gcp' is supported."
        )
