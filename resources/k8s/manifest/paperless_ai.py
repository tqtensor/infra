from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
from pulumi import Output

from resources.cloudflare.tls.tqtensor_com import paper_ai_origin_ca_cert_bundle
from resources.k8s.helm.paperless import paperless_ns
from resources.providers.k8s import k8s_par_2
from resources.utils import decode_password, encode_tls_secret_data
from resources.vm.networking.whitelist import whitelist_cidrs

OPTS = pulumi.ResourceOptions(provider=k8s_par_2)


secrets_file_path = Path(__file__).parent / "secrets" / "paperless.yaml"
paperless_secrets = decode_password(encrypted_yaml=str(secrets_file_path))

paperless_ai_tls_secret = k8s.core.v1.Secret(
    "paperless_ai_tls_secret",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="paper-ai-tls-secret",
        namespace=paperless_ns.metadata["name"],
    ),
    type="kubernetes.io/tls",
    data=Output.all(
        paper_ai_origin_ca_cert_bundle[0].certificate,
        paper_ai_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

paperless_ai_pvc = k8s.core.v1.PersistentVolumeClaim(
    "paperless_ai_pvc",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="paperless-ai-data",
        namespace=paperless_ns.metadata["name"],
    ),
    spec=k8s.core.v1.PersistentVolumeClaimSpecArgs(
        access_modes=["ReadWriteOnce"],
        storage_class_name="scw-bssd",
        resources=k8s.core.v1.VolumeResourceRequirementsArgs(
            requests={"storage": "5Gi"}
        ),
    ),
    opts=OPTS,
)

paperless_ai_deployment = k8s.apps.v1.Deployment(
    "paperless_ai_deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="paperless-ai",
        namespace=paperless_ns.metadata["name"],
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "paperless-ai"},
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "paperless-ai"},
            ),
            spec=k8s.core.v1.PodSpecArgs(
                security_context=k8s.core.v1.PodSecurityContextArgs(
                    fs_group=1000,
                    run_as_user=1000,
                    run_as_group=1000,
                    seccomp_profile=k8s.core.v1.SeccompProfileArgs(
                        type="RuntimeDefault"
                    ),
                ),
                containers=[
                    k8s.core.v1.ContainerArgs(
                        name="paperless-ai",
                        image="clusterzx/paperless-ai:latest",
                        ports=[
                            k8s.core.v1.ContainerPortArgs(
                                container_port=3000, name="http"
                            )
                        ],
                        env=[
                            k8s.core.v1.EnvVarArgs(name="PUID", value="1000"),
                            k8s.core.v1.EnvVarArgs(name="PGID", value="1000"),
                            k8s.core.v1.EnvVarArgs(
                                name="PAPERLESS_AI_PORT", value="3000"
                            ),
                            k8s.core.v1.EnvVarArgs(
                                name="RAG_SERVICE_URL",
                                value="http://paperless-paperless-ngx:8000",
                            ),
                            k8s.core.v1.EnvVarArgs(
                                name="RAG_SERVICE_ENABLED", value="true"
                            ),
                            k8s.core.v1.EnvVarArgs(
                                name="PAPERLESS_API_URL",
                                value="http://paperless-paperless-ngx:8000/api",
                            ),
                            k8s.core.v1.EnvVarArgs(
                                name="PAPERLESS_API_TOKEN",
                                value=paperless_secrets["paperless_api_key"],
                            ),
                        ],
                        volume_mounts=[
                            k8s.core.v1.VolumeMountArgs(
                                name="data",
                                mount_path="/app/data",
                            ),
                            k8s.core.v1.VolumeMountArgs(
                                name="logs",
                                mount_path="/app/logs",
                            ),
                            k8s.core.v1.VolumeMountArgs(
                                name="openapi",
                                mount_path="/app/OPENAPI",
                            ),
                            k8s.core.v1.VolumeMountArgs(
                                name="public-images",
                                mount_path="/app/public/images",
                            ),
                        ],
                        resources=k8s.core.v1.ResourceRequirementsArgs(
                            requests={"memory": "512Mi", "cpu": "100m"},
                            limits={"memory": "2Gi", "cpu": "1000m"},
                        ),
                        security_context=k8s.core.v1.SecurityContextArgs(
                            allow_privilege_escalation=False,
                            capabilities=k8s.core.v1.CapabilitiesArgs(drop=["ALL"]),
                            read_only_root_filesystem=False,
                        ),
                    )
                ],
                volumes=[
                    k8s.core.v1.VolumeArgs(
                        name="data",
                        persistent_volume_claim=k8s.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                            claim_name="paperless-ai-data"
                        ),
                    ),
                    k8s.core.v1.VolumeArgs(
                        name="logs",
                        empty_dir=k8s.core.v1.EmptyDirVolumeSourceArgs(),
                    ),
                    k8s.core.v1.VolumeArgs(
                        name="openapi",
                        empty_dir=k8s.core.v1.EmptyDirVolumeSourceArgs(),
                    ),
                    k8s.core.v1.VolumeArgs(
                        name="public-images",
                        empty_dir=k8s.core.v1.EmptyDirVolumeSourceArgs(),
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions.merge(
        OPTS, pulumi.ResourceOptions(depends_on=[paperless_ns, paperless_ai_pvc])
    ),
)

paperless_ai_service = k8s.core.v1.Service(
    "paperless_ai_service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="paperless-ai",
        namespace=paperless_ns.metadata["name"],
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector={"app": "paperless-ai"},
        ports=[
            k8s.core.v1.ServicePortArgs(
                name="http",
                port=3000,
                target_port=3000,
            )
        ],
        type="ClusterIP",
    ),
    opts=pulumi.ResourceOptions.merge(
        OPTS, pulumi.ResourceOptions(depends_on=[paperless_ai_deployment])
    ),
)

paperless_ai_ingress = k8s.networking.v1.Ingress(
    "paperless_ai_ingress",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="paperless-ai",
        namespace=paperless_ns.metadata["name"],
        annotations={
            "nginx.ingress.kubernetes.io/backend-protocol": "HTTP",
            "nginx.ingress.kubernetes.io/ssl-redirect": "true",
            "nginx.ingress.kubernetes.io/proxy-body-size": "64m",
            "nginx.ingress.kubernetes.io/whitelist-source-range": Output.all(
                *whitelist_cidrs
            ).apply(lambda args: ",".join(args)),
        },
    ),
    spec=k8s.networking.v1.IngressSpecArgs(
        ingress_class_name="nginx",
        tls=[
            k8s.networking.v1.IngressTLSArgs(
                hosts=["paper-ai.tqtensor.com"],
                secret_name="paper-ai-tls-secret",
            )
        ],
        rules=[
            k8s.networking.v1.IngressRuleArgs(
                host="paper-ai.tqtensor.com",
                http=k8s.networking.v1.HTTPIngressRuleValueArgs(
                    paths=[
                        k8s.networking.v1.HTTPIngressPathArgs(
                            path="/",
                            path_type="Prefix",
                            backend=k8s.networking.v1.IngressBackendArgs(
                                service=k8s.networking.v1.IngressServiceBackendArgs(
                                    name="paperless-ai",
                                    port=k8s.networking.v1.ServiceBackendPortArgs(
                                        number=3000
                                    ),
                                )
                            ),
                        )
                    ]
                ),
            )
        ],
    ),
    opts=pulumi.ResourceOptions.merge(
        OPTS,
        pulumi.ResourceOptions(
            depends_on=[
                paperless_ai_service,
                paperless_ai_tls_secret,
            ]
        ),
    ),
)
