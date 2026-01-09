import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(profile="personal", region="eu-central-1", type="resource")


ocone_toon_repository = aws.ecr.Repository(
    "ocone_toon_repository",
    name="ocone-toon",
    image_tag_mutability="MUTABLE",
    image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
        scan_on_push=False,
    ),
    encryption_configurations=[
        aws.ecr.RepositoryEncryptionConfigurationArgs(
            encryption_type="AES256",
        )
    ],
    opts=OPTS,
)
