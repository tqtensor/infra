import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(profile="pixelml", region="us-east-1", type="resource")


bedrock_user = aws.iam.User(
    "bedrock_user", name="victor25k-bedrock-user", force_destroy=True, opts=OPTS
)

bedrock_policy_attachment = aws.iam.UserPolicyAttachment(
    "bedrock_policy_attachment",
    user=bedrock_user.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
    opts=OPTS,
)

bedrock_access_key = aws.iam.AccessKey(
    "bedrock_access_key", user=bedrock_user.name, opts=OPTS
)
