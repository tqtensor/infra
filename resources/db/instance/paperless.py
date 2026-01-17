import pulumi
import pulumiverse_scaleway as scw

from resources.utils import get_options

config = pulumi.Config("scaleway")
project_id = config.require("project_id")

OPTS = get_options(profile="pixelml", region="par-1", provider="scw", protect=False)


paperless_iam_app = scw.IamApplication(
    "paperless_db_app",
    name="paperless-db-app",
    opts=OPTS,
)

paperless_iam_policy = scw.IamPolicy(
    "paperless_db_policy",
    name="paperless-db-policy",
    description="Grants Paperless app access to Serverless SQL Database",
    application_id=paperless_iam_app.id,
    rules=[
        scw.IamPolicyRuleArgs(
            project_ids=[project_id],
            permission_set_names=["ServerlessSQLDatabaseReadWrite"],
        )
    ],
    opts=OPTS,
)

paperless_api_key = scw.IamApiKey(
    "paperless_db_api_key",
    application_id=paperless_iam_app.id,
    opts=OPTS,
)

paperless_db = scw.databases.ServerlessDatabase(
    "paperless_db",
    name="paperless",
    min_cpu=0,
    max_cpu=8,
    opts=pulumi.ResourceOptions(
        provider=OPTS.provider,
        protect=OPTS.protect,
        depends_on=[paperless_iam_policy],
    ),
)
