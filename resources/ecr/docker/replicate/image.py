import subprocess
from pathlib import Path
from typing import Dict, List

import yaml
from pulumi import Output

from resources.ecr.registry import pixelml_us_central_1_registry
from resources.providers import gcp_pixelml_us_central_1
from resources.utils import create_docker_config

_ = Output.all(gcp_pixelml_us_central_1.region).apply(
    lambda args: create_docker_config(
        provider="gcp", server=args[0] + "-docker.pkg.dev"
    )
)

# Consistent prefix for all temporary images
TEMP_PREFIX = "replicate-"


def clone_public_image(
    source_image: str,
    hashes: List[str],
    registry=pixelml_us_central_1_registry,
    gcp_provider=gcp_pixelml_us_central_1,
) -> Dict[str, str]:
    image_uris = {}

    for hash in hashes:
        image_digest = hash
        short_digest = image_digest[:12]

        target_image_name = source_image.split("/")[-1]
        local_temp_image_name = f"{TEMP_PREFIX}{target_image_name}"

        def check_image_exists_and_process(args):
            region, project, repository_id = args
            repository_path = f"{region}-docker.pkg.dev/{project}/{repository_id}"
            target_image = f"{repository_path}/{target_image_name}"
            short_digest_tag = f"{target_image}:{short_digest}"

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
                # Pull the image
                subprocess.run(
                    [
                        "docker",
                        "pull",
                        f"{source_image}@sha256:{image_digest}",
                    ],
                    check=True,
                )

                temp_tag = f"{local_temp_image_name}:{short_digest}"
                subprocess.run(
                    [
                        "docker",
                        "tag",
                        f"{source_image}@sha256:{image_digest}",
                        temp_tag,
                    ],
                    check=True,
                )

                subprocess.run(
                    [
                        "docker",
                        "tag",
                        temp_tag,
                        short_digest_tag,
                    ],
                    check=True,
                )

                print(f"Pushing image to {short_digest_tag}")
                subprocess.run(["docker", "push", short_digest_tag], check=True)
            except Exception as e:
                print(f"Error during process: {e}")
            return "Image processing completed"

        _ = Output.all(
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
        image_uris[image_digest] = image_uri
    return image_uris


configs = yaml.safe_load(open(Path(__file__).parent / "configs.yaml", "r").read())
replicate_image_uris = {}
for source_image, image_config in configs.items():
    replicate_image_uris[source_image] = clone_public_image(
        source_image=image_config["url"], hashes=image_config["hashes"]
    )


def cleanup_all_replicate_images():
    print(f"Cleaning up all {TEMP_PREFIX}* temporary images...")

    try:
        result = subprocess.run(
            [
                "docker",
                "images",
                f"{TEMP_PREFIX}*",
                "--format",
                "{{.Repository}}:{{.Tag}}",
            ],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )

        digest_result = subprocess.run(
            [
                "docker",
                "images",
                "--filter",
                "dangling=false",
                "--format",
                "{{.Repository}}@{{.Digest}}",
            ],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )

        all_images = []

        if result.stdout.strip():
            all_images.extend(result.stdout.strip().split("\n"))

        if digest_result.stdout.strip():
            for line in digest_result.stdout.strip().split("\n"):
                for source_image, image_config in configs.items():
                    if image_config["url"] in line:
                        all_images.append(line)
                        break

        if all_images:
            print(f"Removing {len(all_images)} images...")
            subprocess.run(["docker", "rmi"] + all_images, check=False)
        else:
            print("No temporary images found to clean up.")
    except Exception as e:
        print(f"Error during cleanup: {e}")


Output.all().apply(lambda _: cleanup_all_replicate_images())
