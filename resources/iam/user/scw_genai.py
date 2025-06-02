import pulumi
import pulumiverse_scaleway as scw

from resources.providers import scw_pixelml_par_2
from resources.utils import get_options

OPTS = get_options(profile="pixelml", region="par-2", type="resource", provider="scw")

scw_genai_app = scw.iam.Application(
    "scw_genai_app",
    name="scw-generative-ai-app",
    opts=OPTS,
)

scw_genai_policy = scw.iam.Policy(
    "scw_genai_policy",
    name="generative-ai-policy",
    application_id=scw_genai_app.id,
    rules=[
        scw.iam.PolicyRuleArgs(
            permission_set_names=["GenerativeApisFullAccess"],
            project_ids=[scw_pixelml_par_2.project_id],
        )
    ],
    opts=OPTS,
)

scw_genai_api_key = scw.iam.ApiKey(
    "scw_genai_api_key",
    application_id=scw_genai_app.id,
    opts=OPTS,
)

pulumi.export("IAM: scwGenAI: access_key_id", scw_genai_api_key.access_key)
pulumi.export("IAM: scwGenAI: secret_access_key", scw_genai_api_key.secret_key)
