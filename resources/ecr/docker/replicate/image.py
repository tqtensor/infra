import subprocess
from typing import Dict, Optional

from pulumi import Output

from resources.ecr.registry import pixelml_us_central_1_registry
from resources.providers import gcp_pixelml_us_central_1
from resources.utils import create_docker_config

_ = Output.all(gcp_pixelml_us_central_1.region).apply(
    lambda args: create_docker_config(
        provider="gcp", server=args[0] + "-docker.pkg.dev"
    )
)


def clone_public_image(
    source_image: str,
    image_digest: str,
    target_image_name: Optional[str] = None,
    registry=pixelml_us_central_1_registry,
    gcp_provider=gcp_pixelml_us_central_1,
) -> Dict[str, Output]:
    short_digest = image_digest[:12]

    if not target_image_name:
        target_image_name = source_image.split("/")[-1]

    def check_image_exists_and_process(args):
        region, project, repository_id = args
        repository_path = f"{region}-docker.pkg.dev/{project}/{repository_id}"
        target_image = f"{repository_path}/{target_image_name}"
        short_digest_tag = f"{target_image}:{short_digest}"
        latest_tag = f"{target_image}:latest"

        try:
            result = subprocess.run(
                [
                    "gcloud",
                    "artifacts",
                    "docker",
                    "images",
                    "describe",
                    short_digest_tag,
                    "--project",
                    project,
                    "--quiet",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            if result.returncode == 0:
                print(
                    f"Image {short_digest_tag} already exists in Artifact Registry. Skipping pull and push."
                )
                return "Image already exists in Artifact Registry"
        except Exception as e:
            print(f"Error checking image existence: {e}")

        print(f"Pulling base image {source_image}@sha256:{image_digest}")

        try:
            subprocess.run(
                [
                    "docker",
                    "pull",
                    f"{source_image}@sha256:{image_digest}",
                ],
                check=True,
            )

            subprocess.run(
                [
                    "docker",
                    "tag",
                    f"{source_image}@sha256:{image_digest}",
                    short_digest_tag,
                ],
                check=True,
            )

            # Tag as latest
            subprocess.run(
                [
                    "docker",
                    "tag",
                    f"{source_image}@sha256:{image_digest}",
                    latest_tag,
                ],
                check=True,
            )

            print(f"Pushing image to {short_digest_tag}")
            subprocess.run(["docker", "push", short_digest_tag], check=True)

            print(f"Pushing image to {latest_tag}")
            subprocess.run(["docker", "push", latest_tag], check=True)
        finally:
            print("Cleaning up local images...")
            try:
                subprocess.run(
                    [
                        "docker",
                        "rmi",
                        f"{source_image}@sha256:{image_digest}",
                    ],
                    check=False,
                )

                subprocess.run(["docker", "rmi", short_digest_tag], check=False)
                subprocess.run(["docker", "rmi", latest_tag], check=False)
            except Exception as e:
                print(f"Error during cleanup: {e}")

        return "Image pulled, tagged, pushed, and cleaned up successfully"

    tagged_and_pushed = Output.all(
        gcp_provider.region,
        gcp_provider.project,
        registry.repository_id,
    ).apply(check_image_exists_and_process)

    image_uri = Output.concat(
        gcp_provider.region,
        "-docker.pkg.dev/",
        gcp_provider.project,
        "/",
        registry.repository_id,
        f"/{target_image_name}",
    )
    return {
        "image_uri": image_uri,
        "operation_status": tagged_and_pushed,
    }


whisper_diarization_image_uri = clone_public_image(
    source_image="r8.im/thomasmol/whisper-diarization",
    image_digest="d8bc5908738ebd84a9bb7d77d94b9c5e5a3d867886791d7171ddb60455b4c6af",
)["image_uri"]

moondream2_image_uri = clone_public_image(
    source_image="r8.im/lucataco/moondream2",
    image_digest="72ccb656353c348c1385df54b237eeb7bfa874bf11486cf0b9473e691b662d31",
)["image_uri"]
