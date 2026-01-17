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

# Exports for connection details
pulumi.export("paperless_db_endpoint", paperless_db.endpoint)
pulumi.export("paperless_db_name", paperless_db.name)
pulumi.export("paperless_db_user", paperless_iam_app.id)
pulumi.export(
    "paperless_db_password", pulumi.Output.secret(paperless_api_key.secret_key)
)

# Full connection string (marked as secret)
pulumi.export(
    "paperless_db_connection_string",
    pulumi.Output.secret(
        pulumi.Output.all(
            paperless_iam_app.id, paperless_api_key.secret_key, paperless_db.endpoint
        ).apply(
            lambda args: f"postgres://{args[0]}:{args[1]}@{args[2].replace('postgres://', '')}"
        )
    ),
)

# Parsed connection components for convenience
pulumi.export(
    "paperless_db_host",
    paperless_db.endpoint.apply(
        lambda endpoint: (
            endpoint.split("://")[1].split(":")[0]
            if "://" in endpoint
            else endpoint.split(":")[0]
        )
    ),
)

pulumi.export(
    "paperless_db_port",
    paperless_db.endpoint.apply(
        lambda endpoint: (
            endpoint.split(":")[-1].split("/")[0] if ":" in endpoint else "5432"
        )
    ),
)
