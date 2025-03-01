import json

import pulumi_aws as aws
import pulumi_gcp as gcp
from pulumi import Output

from resources.kms import gke_key
from resources.providers import gcp_pixelml_eu_west_1
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="eu-central-1", type="resource", protect=False
)


gke_api_role = aws.iam.Role(
    "gke_api_role",
    name="gke-api-role",
    assume_role_policy=Output.all(
        gcp.organizations.get_project(project_id=gcp_pixelml_eu_west_1.project).number
    ).apply(
        lambda args: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "",
                        "Effect": "Allow",
                        "Principal": {"Federated": "accounts.google.com"},
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {
                                "accounts.google.com:sub": f"service-{args[0]}@gcp-sa-gkemulticloud.iam.gserviceaccount.com"
                            }
                        },
                    }
                ],
            }
        )
    ),
    opts=OPTS,
)

gke_api_policy = aws.iam.Policy(
    "gke_api_policy",
    name="gke-api-policy",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Action": [
                        "autoscaling:CreateAutoScalingGroup",
                        "autoscaling:CreateOrUpdateTags",
                        "autoscaling:DeleteAutoScalingGroup",
                        "autoscaling:DeleteTags",
                        "autoscaling:DescribeAutoScalingGroups",
                        "autoscaling:DisableMetricsCollection",
                        "autoscaling:EnableMetricsCollection",
                        "autoscaling:TerminateInstanceInAutoScalingGroup",
                        "autoscaling:UpdateAutoScalingGroup",
                        "ec2:AuthorizeSecurityGroupEgress",
                        "ec2:AuthorizeSecurityGroupIngress",
                        "ec2:CreateLaunchTemplate",
                        "ec2:CreateNetworkInterface",
                        "ec2:CreateSecurityGroup",
                        "ec2:CreateTags",
                        "ec2:CreateVolume",
                        "ec2:DeleteLaunchTemplate",
                        "ec2:DeleteNetworkInterface",
                        "ec2:DeleteSecurityGroup",
                        "ec2:DeleteTags",
                        "ec2:DeleteVolume",
                        "ec2:DescribeAccountAttributes",
                        "ec2:DescribeInstances",
                        "ec2:DescribeInternetGateways",
                        "ec2:DescribeKeyPairs",
                        "ec2:DescribeLaunchTemplates",
                        "ec2:DescribeNetworkInterfaces",
                        "ec2:DescribeSecurityGroupRules",
                        "ec2:DescribeSecurityGroups",
                        "ec2:DescribeSubnets",
                        "ec2:DescribeVpcs",
                        "ec2:GetConsoleOutput",
                        "ec2:ModifyInstanceAttribute",
                        "ec2:ModifyNetworkInterfaceAttribute",
                        "ec2:RevokeSecurityGroupEgress",
                        "ec2:RevokeSecurityGroupIngress",
                        "ec2:RunInstances",
                        "elasticloadbalancing:AddTags",
                        "elasticloadbalancing:CreateListener",
                        "elasticloadbalancing:CreateLoadBalancer",
                        "elasticloadbalancing:CreateTargetGroup",
                        "elasticloadbalancing:DeleteListener",
                        "elasticloadbalancing:DeleteLoadBalancer",
                        "elasticloadbalancing:DeleteTargetGroup",
                        "elasticloadbalancing:DescribeListeners",
                        "elasticloadbalancing:DescribeLoadBalancers",
                        "elasticloadbalancing:DescribeTargetGroups",
                        "elasticloadbalancing:DescribeTargetHealth",
                        "elasticloadbalancing:ModifyTargetGroupAttributes",
                        "elasticloadbalancing:RemoveTags",
                        "iam:AWSServiceName",
                        "iam:CreateServiceLinkedRole",
                        "iam:GetInstanceProfile",
                        "iam:PassRole",
                        "kms:DescribeKey",
                        "kms:Encrypt",
                        "kms:GenerateDataKeyWithoutPlaintext",
                    ],
                    "Resource": "*",
                }
            ],
        }
    ),
    opts=OPTS,
)

gke_api_role_policy_attachment = aws.iam.RolePolicyAttachment(
    "gke_role_policy_attachment",
    role=gke_api_role.name,
    policy_arn=gke_api_policy.arn,
    opts=OPTS,
)

gke_control_plane_role = aws.iam.Role(
    "gke_control_plane_role",
    name="gke-control-plane-role",
    assume_role_policy={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    },
    opts=OPTS,
)

gke_control_plane_policy = aws.iam.Policy(
    "gke_control_plane_policy",
    name="gke-control-plane-policy",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Action": [
                        "autoscaling:DescribeAutoScalingGroups",
                        "autoscaling:DescribeAutoScalingInstances",
                        "autoscaling:DescribeLaunchConfigurations",
                        "autoscaling:DescribeTags",
                        "autoscaling:SetDesiredCapacity",
                        "autoscaling:TerminateInstanceInAutoScalingGroup",
                        "ec2:AttachNetworkInterface",
                        "ec2:AttachVolume",
                        "ec2:AuthorizeSecurityGroupIngress",
                        "ec2:CreateRoute",
                        "ec2:CreateSecurityGroup",
                        "ec2:CreateSnapshot",
                        "ec2:CreateTags",
                        "ec2:CreateVolume",
                        "ec2:DeleteRoute",
                        "ec2:DeleteSecurityGroup",
                        "ec2:DeleteSnapshot",
                        "ec2:DeleteTags",
                        "ec2:DeleteVolume",
                        "ec2:DescribeAccountAttributes",
                        "ec2:DescribeAvailabilityZones",
                        "ec2:DescribeDhcpOptions",
                        "ec2:DescribeInstanceTypes",
                        "ec2:DescribeInstances",
                        "ec2:DescribeInternetGateways",
                        "ec2:DescribeLaunchTemplateVersions",
                        "ec2:DescribeRegions",
                        "ec2:DescribeRouteTables",
                        "ec2:DescribeSecurityGroups",
                        "ec2:DescribeSnapshots",
                        "ec2:DescribeSubnets",
                        "ec2:DescribeTags",
                        "ec2:DescribeVolumes",
                        "ec2:DescribeVolumesModifications",
                        "ec2:DescribeVpcs",
                        "ec2:DetachVolume",
                        "ec2:ModifyInstanceAttribute",
                        "ec2:ModifyVolume",
                        "ec2:RevokeSecurityGroupIngress",
                        "elasticfilesystem:CreateAccessPoint",
                        "elasticfilesystem:DeleteAccessPoint",
                        "elasticfilesystem:DescribeAccessPoints",
                        "elasticfilesystem:DescribeFileSystems",
                        "elasticfilesystem:DescribeMountTargets",
                        "elasticloadbalancing:AddTags",
                        "elasticloadbalancing:ApplySecurityGroupsToLoadBalancer",
                        "elasticloadbalancing:AttachLoadBalancerToSubnets",
                        "elasticloadbalancing:ConfigureHealthCheck",
                        "elasticloadbalancing:CreateListener",
                        "elasticloadbalancing:CreateLoadBalancer",
                        "elasticloadbalancing:CreateLoadBalancerListeners",
                        "elasticloadbalancing:CreateLoadBalancerPolicy",
                        "elasticloadbalancing:CreateTargetGroup",
                        "elasticloadbalancing:DeleteListener",
                        "elasticloadbalancing:DeleteLoadBalancer",
                        "elasticloadbalancing:DeleteLoadBalancerListeners",
                        "elasticloadbalancing:DeleteTargetGroup",
                        "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
                        "elasticloadbalancing:DeregisterTargets",
                        "elasticloadbalancing:DescribeListeners",
                        "elasticloadbalancing:DescribeLoadBalancerAttributes",
                        "elasticloadbalancing:DescribeLoadBalancerPolicies",
                        "elasticloadbalancing:DescribeLoadBalancers",
                        "elasticloadbalancing:DescribeTargetGroups",
                        "elasticloadbalancing:DescribeTargetHealth",
                        "elasticloadbalancing:DetachLoadBalancerFromSubnets",
                        "elasticloadbalancing:ModifyListener",
                        "elasticloadbalancing:ModifyLoadBalancerAttributes",
                        "elasticloadbalancing:ModifyTargetGroup",
                        "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
                        "elasticloadbalancing:RegisterTargets",
                        "elasticloadbalancing:SetLoadBalancerPoliciesForBackendServer",
                        "elasticloadbalancing:SetLoadBalancerPoliciesOfListener",
                        "kms:CreateGrant",
                        "kms:Decrypt",
                        "kms:Encrypt",
                        "kms:GrantIsForAWSResource",
                    ],
                    "Resource": "*",
                }
            ],
        }
    ),
    opts=OPTS,
)

gke_control_plane_role_policy_attachment = aws.iam.RolePolicyAttachment(
    "gke_control_plane_role_policy_attachment",
    role=gke_control_plane_role.name,
    policy_arn=gke_control_plane_policy.arn,
    opts=OPTS,
)

gke_node_pool_role = aws.iam.Role(
    "gke_node_pool_role",
    name="gke-node-pool-role",
    assume_role_policy={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    },
    opts=OPTS,
)

gke_node_pool_policy = aws.iam.Policy(
    "gke_node_pool_policy",
    name="gke-node-pool-policy",
    policy=Output.all(gke_key.arn).apply(
        lambda args: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {"Effect": "Allow", "Action": ["kms:Decrypt"], "Resource": args[0]}
                ],
            }
        )
    ),
    opts=OPTS,
)

gke_node_pool_role_policy_attachment = aws.iam.RolePolicyAttachment(
    "gke_node_pool_role_policy_attachment",
    role=gke_node_pool_role.name,
    policy_arn=gke_node_pool_policy.arn,
    opts=OPTS,
)

gke_control_plane_profile = aws.iam.InstanceProfile(
    "gke_control_plane_profile",
    name="gke-control-plane-profile",
    role=gke_control_plane_role.id,
    opts=OPTS,
)

gke_node_pool_profile = aws.iam.InstanceProfile(
    "gke_node_pool_profile",
    name="gke-node-pool-profile",
    role=gke_node_pool_role.id,
    opts=OPTS,
)
