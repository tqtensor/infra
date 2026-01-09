import pulumi_aws as aws

from resources.sagemaker.role import ocone_sagemaker_execution_role
from resources.utils import get_options

OPTS = get_options(profile="personal", region="eu-central-1", type="resource")


ocone_sagemaker_domain = aws.sagemaker.Domain(
    "ocone_sagemaker_domain",
    domain_name="ocone-studio",
    auth_mode="IAM",
    vpc_id="vpc-578d773d",
    subnet_ids=["subnet-13963479"],
    app_network_access_type="PublicInternetOnly",
    default_user_settings=aws.sagemaker.DomainDefaultUserSettingsArgs(
        execution_role=ocone_sagemaker_execution_role.arn,
        studio_web_portal="ENABLED",
    ),
    opts=OPTS,
)
