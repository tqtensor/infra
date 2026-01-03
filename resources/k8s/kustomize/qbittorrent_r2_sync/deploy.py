import base64
import hashlib
from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
from pulumi import Output

from resources.iam.user.r2 import tqtensor_homelab_r2_token
from resources.providers.k8s import k8s_par_2

OPTS = pulumi.ResourceOptions(provider=k8s_par_2)


def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


qbittorrent_ns_name = "torrent"

account_id = pulumi.Config().require("cloudflareAccountId")

qbittorrent_r2_sync_secrets = k8s.core.v1.Secret(
    "qbittorrent_r2_sync_secrets",
    metadata={
        "name": "qbittorrent-r2-sync-secrets",
        "namespace": qbittorrent_ns_name,
    },
    data=Output.all(
        tqtensor_homelab_r2_token.id,
        tqtensor_homelab_r2_token.value,
    ).apply(
        lambda args: {
            "r2_access_key_id": base64.b64encode(args[0].encode()).decode(),
            "r2_secret_access_key": base64.b64encode(
                sha256_hash(args[1]).encode()
            ).decode(),
            "r2_endpoint": base64.b64encode(
                f"https://{account_id}.r2.cloudflarestorage.com".encode()
            ).decode(),
        }
    ),
    opts=OPTS,
)

base_dir = Path(__file__).parent / "base"

qbittorrent_r2_sync_kustomize = k8s.kustomize.Directory(
    "qbittorrent_r2_sync_kustomize",
    directory=base_dir.as_posix(),
    opts=pulumi.ResourceOptions(
        provider=k8s_par_2,
        depends_on=[qbittorrent_r2_sync_secrets],
    ),
)
