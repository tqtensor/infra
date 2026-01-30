import pulumi
import pulumi_kubernetes as k8s
from pulumi import Output

from resources.cloudflare.tls.tqtensor_com import code_origin_ca_cert_bundle
from resources.providers.k8s import k8s_par_2
from resources.utils import encode_tls_secret_data
from resources.vm.networking.whitelist import whitelist_cidrs

OPTS = pulumi.ResourceOptions(provider=k8s_par_2)


code_server_ns = k8s.core.v1.Namespace(
    "code_server_ns",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="code-server",
    ),
    opts=OPTS,
)

code_server_tls_secret = k8s.core.v1.Secret(
    "code_server_tls_secret",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="code-server-tls-secret",
        namespace=code_server_ns.metadata["name"],
    ),
    type="kubernetes.io/tls",
    data=Output.all(
        code_origin_ca_cert_bundle[0].certificate,
        code_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=pulumi.ResourceOptions.merge(
        OPTS, pulumi.ResourceOptions(depends_on=[code_server_ns])
    ),
)

code_server_pvc = k8s.core.v1.PersistentVolumeClaim(
    "code_server_pvc",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="code-server-data",
        namespace=code_server_ns.metadata["name"],
    ),
    spec=k8s.core.v1.PersistentVolumeClaimSpecArgs(
        access_modes=["ReadWriteOnce"],
        storage_class_name="scw-bssd",
        resources=k8s.core.v1.VolumeResourceRequirementsArgs(
            requests={"storage": "5Gi"}
        ),
    ),
    opts=pulumi.ResourceOptions.merge(
        OPTS, pulumi.ResourceOptions(depends_on=[code_server_ns])
    ),
)

code_server_deployment = k8s.apps.v1.Deployment(
    "code_server_deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="code-server",
        namespace=code_server_ns.metadata["name"],
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(
            match_labels={"app": "code-server"},
        ),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(
                labels={"app": "code-server"},
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
                        name="code-server",
                        image="codercom/code-server:latest",
                        args=["--auth", "none", "--bind-addr", "0.0.0.0:8080"],
                        ports=[
                            k8s.core.v1.ContainerPortArgs(
                                container_port=8080, name="http"
                            )
                        ],
                        volume_mounts=[
                            k8s.core.v1.VolumeMountArgs(
                                name="data",
                                mount_path="/home/coder",
                            ),
                        ],
                        resources=k8s.core.v1.ResourceRequirementsArgs(
                            requests={"memory": "2Gi", "cpu": "512m"},
                            limits={"memory": "16Gi", "cpu": "8"},
                        ),
                        security_context=k8s.core.v1.SecurityContextArgs(
                            read_only_root_filesystem=False,
                        ),
                    )
                ],
                volumes=[
                    k8s.core.v1.VolumeArgs(
                        name="data",
                        persistent_volume_claim=k8s.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                            claim_name="code-server-data"
                        ),
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions.merge(
        OPTS,
        pulumi.ResourceOptions(depends_on=[code_server_ns, code_server_pvc]),
    ),
)

code_server_service = k8s.core.v1.Service(
    "code_server_service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="code-server",
        namespace=code_server_ns.metadata["name"],
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector={"app": "code-server"},
        ports=[
            k8s.core.v1.ServicePortArgs(
                name="http",
                port=8080,
                target_port=8080,
            )
        ],
        type="ClusterIP",
    ),
    opts=pulumi.ResourceOptions.merge(
        OPTS, pulumi.ResourceOptions(depends_on=[code_server_deployment])
    ),
)

code_server_ingress = k8s.networking.v1.Ingress(
    "code_server_ingress",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="code-server",
        namespace=code_server_ns.metadata["name"],
        annotations={
            "nginx.ingress.kubernetes.io/backend-protocol": "HTTP",
            "nginx.ingress.kubernetes.io/ssl-redirect": "true",
            "nginx.ingress.kubernetes.io/proxy-read-timeout": "3600",
            "nginx.ingress.kubernetes.io/proxy-send-timeout": "3600",
            "nginx.ingress.kubernetes.io/whitelist-source-range": Output.all(
                *whitelist_cidrs
            ).apply(lambda args: ",".join(args)),
        },
    ),
    spec=k8s.networking.v1.IngressSpecArgs(
        ingress_class_name="nginx",
        tls=[
            k8s.networking.v1.IngressTLSArgs(
                hosts=["code.tqtensor.com"],
                secret_name="code-server-tls-secret",
            )
        ],
        rules=[
            k8s.networking.v1.IngressRuleArgs(
                host="code.tqtensor.com",
                http=k8s.networking.v1.HTTPIngressRuleValueArgs(
                    paths=[
                        k8s.networking.v1.HTTPIngressPathArgs(
                            path="/",
                            path_type="Prefix",
                            backend=k8s.networking.v1.IngressBackendArgs(
                                service=k8s.networking.v1.IngressServiceBackendArgs(
                                    name="code-server",
                                    port=k8s.networking.v1.ServiceBackendPortArgs(
                                        number=8080
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
                code_server_service,
                code_server_tls_secret,
            ]
        ),
    ),
)
