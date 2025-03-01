import pulumi_gcp as gcp

from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="asia-east-1", type="resource", provider="gcp"
)


asia_east_1_cluster = gcp.container.Cluster(
    "asia_east_1_cluster",
    name="asia-east-1-cluster",
    initial_node_count=1,
    remove_default_node_pool=True,
    enable_intranode_visibility=True,
    release_channel=gcp.container.ClusterReleaseChannelArgs(
        channel="REGULAR",
    ),
    opts=OPTS,
)

asia_east_1_default_pool = gcp.container.NodePool(
    "asia_east_1_default_pool",
    name="asia-east-1-default-pool",
    cluster=asia_east_1_cluster.name,
    initial_node_count=1,
    autoscaling=gcp.container.NodePoolAutoscalingArgs(
        min_node_count=1,
        max_node_count=5,
    ),
    management=gcp.container.NodePoolManagementArgs(
        auto_repair=True,
        auto_upgrade=True,
    ),
    node_config=gcp.container.NodePoolNodeConfigArgs(
        machine_type="e2-standard-4",
        disk_size_gb=100,
        disk_type="pd-standard",
        oauth_scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
        ],
        image_type="COS_CONTAINERD",
    ),
    opts=OPTS,
)

asia_east_1_gpu_pool = gcp.container.NodePool(
    "asia_east_1_gpu_pool",
    name="asia-east-1-gpu-pool",
    cluster=asia_east_1_cluster.name,
    initial_node_count=0,
    autoscaling=gcp.container.NodePoolAutoscalingArgs(
        min_node_count=0,
        max_node_count=5,
    ),
    management=gcp.container.NodePoolManagementArgs(
        auto_repair=True,
        auto_upgrade=True,
    ),
    node_config=gcp.container.NodePoolNodeConfigArgs(
        machine_type="g2-standard-8",
        disk_size_gb=100,
        disk_type="pd-ssd",
        spot=True,
        oauth_scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
        ],
        guest_accelerators=[
            gcp.container.NodePoolNodeConfigGuestAcceleratorArgs(
                type="nvidia-l4",
                count=1,
            )
        ],
        image_type="COS_CONTAINERD",
        labels={
            "cloud.google.com/gke-accelerator": "nvidia-l4",
            "cloud.google.com/gke-spot": "true",
        },
        taints=[
            gcp.container.NodePoolNodeConfigTaintArgs(
                key="nvidia.com/gpu",
                value="present",
                effect="NO_SCHEDULE",
            )
        ],
    ),
    opts=OPTS,
)
