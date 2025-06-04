from typing import Optional

import pulumi
import pulumi_gcp as gcp
from pulumiverse_scaleway import registry


class BaseImageRef(pulumi.ComponentResource):
    def __init__(
        self,
        resource_type: str,
        name: str,
        tag: Optional[str] = None,
        uri: Optional[str] = None,
        opts: pulumi.ResourceOptions = None,
    ):
        super().__init__(resource_type, name, {}, opts)
        self.uri = uri
        self.name = name
        self.tag = tag
        self.register_outputs({"uri": self.uri, "name": self.name, "tag": self.tag})


class ScalewayImage(BaseImageRef):
    def __init__(
        self,
        name: str,
        tag: str,
        namespace: registry.Namespace,
        opts: pulumi.ResourceOptions = None,
    ):
        uri = namespace.endpoint.apply(lambda endpoint: f"{endpoint}/{name}:{tag}")
        super().__init__("custom:scaleway:ImageRef", name, tag, uri, opts)


class GCPImage(BaseImageRef):
    def __init__(
        self,
        name: str,
        provider: gcp.Provider,
        repository: gcp.artifactregistry.Repository,
        tag: Optional[str] = None,
        opts: pulumi.ResourceOptions = None,
    ):
        if tag is None:
            uri = pulumi.Output.all(
                provider.region, provider.project, repository.name, name
            ).apply(
                lambda args: f"{args[0]}-docker.pkg.dev/{args[1]}/{args[2]}/{args[3]}"
            )
        else:
            uri = pulumi.Output.all(
                provider.region, provider.project, repository.name, name, tag
            ).apply(
                lambda args: f"{args[0]}-docker.pkg.dev/{args[1]}/{args[2]}/{args[3]}:{args[4]}"
            )
        super().__init__("custom:gcp:ImageRef", name, tag, uri, opts)
