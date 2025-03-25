import datetime as dt
import pathlib

import pulumi_docker_build as docker_build
from pulumi import Output

from resources.ecr.registry import pixelml_eu_west_4_registry
from resources.providers import gcp_pixelml_eu_west_4
from resources.utils import create_docker_config

_ = Output.all(gcp_pixelml_eu_west_4.region).apply(
    lambda args: create_docker_config(
        provider="gcp", server=args[0] + "-docker.pkg.dev"
    )
)

current_file_path = pathlib.Path(__file__).resolve()

image_tag = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y%m%d%H%M%S")

flan_t5_base_image = docker_build.Image(
    "flan_t5_base_image",
    tags=[
        Output.concat(
            gcp_pixelml_eu_west_4.region,
            "-docker.pkg.dev/",
            gcp_pixelml_eu_west_4.project,
            "/",
            pixelml_eu_west_4_registry.repository_id,
            f"/flan_t5_base:{image_tag}",
        ),
        Output.concat(
            gcp_pixelml_eu_west_4.region,
            "-docker.pkg.dev/",
            gcp_pixelml_eu_west_4.project,
            "/",
            pixelml_eu_west_4_registry.repository_id,
            "/flan_t5_base:latest",
        ),
    ],
    context=docker_build.BuildContextArgs(
        location=str(current_file_path.parent / "flan_t5_base"),
    ),
    dockerfile=docker_build.DockerfileArgs(
        location=str(current_file_path.parent / "flan_t5_base" / "Dockerfile"),
    ),
    platforms=[
        docker_build.Platform.LINUX_AMD64,
    ],
    push=True,
)
