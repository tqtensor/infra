import base64
from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
from pulumi import Output

from resources.k8s.providers import k8s_provider_par_2
from resources.storage import (
    s3gw_blob_container,
    s3gw_storage_account,
    s3gw_storage_keys,
)

OPTS = pulumi.ResourceOptions(provider=k8s_provider_par_2)


az_s3gw_yaml_path = str(Path(__file__).parent / "artifacts" / "az_s3gw.yaml")

bucket_claim_name = "az-s3gw-bucket-claim"
bucket_prefix = "az-s3gw-data"


def transform_noobaa_resources(res: dict):
    if res["kind"] == "Secret" and res["metadata"]["name"] == "azure-storage-secret":
        res["data"]["AccountName"] = Output.all(s3gw_storage_account.name).apply(
            lambda args: base64.b64encode(args[0].encode()).decode()
        )
        res["data"]["AccountKey"] = Output.all(s3gw_storage_keys.keys[0].value).apply(
            lambda args: base64.b64encode(args[0].encode()).decode()
        )

    if res["kind"] == "BackingStore":
        res["spec"]["azureBlob"]["targetBlobContainer"] = s3gw_blob_container.name

    if res["kind"] == "ObjectBucketClaim":
        res["metadata"]["name"] = bucket_claim_name
        res["spec"]["generateBucketName"] = bucket_prefix
    return res


az_s3gw = k8s.yaml.ConfigFile(
    "az_s3gw",
    file=az_s3gw_yaml_path,
    transformations=[transform_noobaa_resources],
    opts=OPTS,
)

az_s3gw_bucket_configmap = k8s.core.v1.ConfigMap.get(
    "az_s3gw_bucket_configmap",
    f"noobaa/{bucket_claim_name}",
    opts=pulumi.ResourceOptions(provider=k8s_provider_par_2, depends_on=[az_s3gw]),
)

az_s3gw_bucket_secret = k8s.core.v1.Secret.get(
    "az_s3gw_bucket_secret",
    f"noobaa/{bucket_claim_name}",
    opts=pulumi.ResourceOptions(provider=k8s_provider_par_2, depends_on=[az_s3gw]),
)

pulumi.export(
    "S3: Azure: bucket_name",
    az_s3gw_bucket_configmap.data.apply(lambda data: data.get("BUCKET_NAME")),
)

pulumi.export(
    "S3: Azure: aws_access_key_id",
    az_s3gw_bucket_secret.data.apply(
        lambda data: Output.all(data.get("AWS_ACCESS_KEY_ID")).apply(
            lambda keys: base64.b64decode(keys[0]).decode() if keys[0] else None
        )
    ),
)

pulumi.export(
    "S3: Azure: aws_secret_access_key",
    az_s3gw_bucket_secret.data.apply(
        lambda data: Output.all(data.get("AWS_SECRET_ACCESS_KEY")).apply(
            lambda keys: base64.b64decode(keys[0]).decode() if keys[0] else None
        )
    ),
)
