import pathlib

import pulumi_docker_build as docker_build
from pulumi import Output

from resources.ecr.registry import pixelml_us_central_1_registry
from resources.providers import gcp_pixelml_us_central_1
from resources.utils import create_docker_config

_ = Output.all(gcp_pixelml_us_central_1.region).apply(
    lambda args: create_docker_config(
        provider="gcp", server=args[0] + "-docker.pkg.dev"
    )
)

current_file_path = pathlib.Path(__file__).resolve()

ragflow_image = docker_build.Image(
    "ragflow_image",
    tags=[
        Output.concat(
            gcp_pixelml_us_central_1.region,
            "-docker.pkg.dev/",
            gcp_pixelml_us_central_1.project,
            "/",
            pixelml_us_central_1_registry.repository_id,
            "/ragflow:latest",
        ),
    ],
    context=docker_build.BuildContextArgs(
        location=str(current_file_path.parent),
    ),
    dockerfile=docker_build.DockerfileArgs(
        location=str(current_file_path.parent / "Dockerfile"),
    ),
    platforms=[
        docker_build.Platform.LINUX_AMD64,
    ],
    push=True,
)

ragflow_image_uri = Output.all(
    gcp_pixelml_us_central_1.region,
    gcp_pixelml_us_central_1.project,
    pixelml_us_central_1_registry.repository_id,
    ragflow_image.digest,
).apply(lambda args: f"{args[0]}-docker.pkg.dev/{args[1]}/{args[2]}/ragflow@{args[3]}")
