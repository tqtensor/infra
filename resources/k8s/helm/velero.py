import base64
from pathlib import Path
from typing import Dict

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.iam.user import velero_access_key
from resources.k8s.providers import k8s_provider_par_2
from resources.storage.bucket.s3 import velero_bucket

OPTS = pulumi.ResourceOptions(provider=k8s_provider_par_2)


velero_ns = k8s.core.v1.Namespace("velero_ns", metadata={"name": "velero"}, opts=OPTS)

velero_aws_credentials = k8s.core.v1.Secret(
    "velero_aws_credentials",
    metadata={
        "name": "velero-aws-credentials",
        "namespace": velero_ns.metadata["name"],
    },
    data=Output.all(
        velero_access_key.id,
        velero_access_key.secret,
    ).apply(
        lambda args: {
            "s3": base64.b64encode(
                f"[default]\naws_access_key_id={args[0]}\naws_secret_access_key={args[1]}\n".encode()
            ).decode(),
        }
    ),
    opts=OPTS,
)

values_file_path = Path(__file__).parent / "values" / "velero.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    def prepare_values(
        bucket,
        region,
    ) -> Dict[str, str]:
        return {
            "bucket": bucket,
            "region": region,
        }

    values = Output.all(
        velero_bucket.id,
        velero_bucket.region,
    ).apply(
        lambda args: prepare_values(
            args[0],
            args[1],
        )
    )

    chart_values["configuration"]["backupStorageLocation"][0]["bucket"] = values[
        "bucket"
    ]
    chart_values["configuration"]["backupStorageLocation"][0]["config"][
        "region"
    ] = values["region"]

    chart_values["configuration"]["volumeSnapshotLocation"][0]["config"][
        "region"
    ] = values["region"]

velero_release = k8s.helm.v3.Release(
    "velero",
    k8s.helm.v3.ReleaseArgs(
        chart="velero",
        version="10.0.1",
        name="vmware-tanzu",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://vmware-tanzu.github.io/helm-charts",
        ),
        namespace=velero_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_par_2,
        depends_on=[velero_ns, velero_aws_credentials],
    ),
)
