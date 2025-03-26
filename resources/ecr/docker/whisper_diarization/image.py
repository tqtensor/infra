import subprocess

from pulumi import Output

from resources.ecr.registry import pixelml_us_central_1_registry
from resources.providers import gcp_pixelml_us_central_1
from resources.utils import create_docker_config

_ = Output.all(gcp_pixelml_us_central_1.region).apply(
    lambda args: create_docker_config(
        provider="gcp", server=args[0] + "-docker.pkg.dev"
    )
)

image_tag = "d8bc5908738ebd84a9bb7d77d94b9c5e5a3d867886791d7171ddb60455b4c6af"

subprocess.run(
    ["docker", "pull", f"r8.im/thomasmol/whisper-diarization@sha256:{image_tag}"],
    check=True,
)


def tag_and_push_image(args):
    region, project, repository_id = args

    # Create the tag with the short digest
    short_digest_tag = f"{region}-docker.pkg.dev/{project}/{repository_id}/whisper-diarization:{image_tag[:12]}"
    subprocess.run(
        [
            "docker",
            "tag",
            f"r8.im/thomasmol/whisper-diarization@sha256:{image_tag}",
            short_digest_tag,
        ],
        check=True,
    )

    # Create the latest tag
    latest_tag = (
        f"{region}-docker.pkg.dev/{project}/{repository_id}/whisper-diarization:latest"
    )
    subprocess.run(
        [
            "docker",
            "tag",
            f"r8.im/thomasmol/whisper-diarization@sha256:{image_tag}",
            latest_tag,
        ],
        check=True,
    )

    # Push both tags
    subprocess.run(["docker", "push", short_digest_tag], check=True)
    subprocess.run(["docker", "push", latest_tag], check=True)
    return "Image tagged and pushed successfully"


tagged_and_pushed = Output.all(
    gcp_pixelml_us_central_1.region,
    gcp_pixelml_us_central_1.project,
    pixelml_us_central_1_registry.repository_id,
).apply(tag_and_push_image)

whisper_diarization_image_uri = Output.concat(
    gcp_pixelml_us_central_1.region,
    "-docker.pkg.dev/",
    gcp_pixelml_us_central_1.project,
    "/",
    pixelml_us_central_1_registry.repository_id,
    "/whisper-diarization",
)
