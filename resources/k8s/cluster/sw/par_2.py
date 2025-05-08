import pulumiverse_scaleway as scw

from resources.utils import get_options

OPTS = get_options(profile="pixelml", region="par-2", type="resource", provider="sw")
REGION = "fr-par"
ZONE = "fr-par-2"


par_2_pn = scw.network.PrivateNetwork(
    "par_2_pn", name="kube-network-par-2", region=REGION, opts=OPTS
)

nginx_ip_par_2 = scw.loadbalancers.Ip("nginx_ip_par_2", zone=ZONE, opts=OPTS)

nginx_lb_par_2 = scw.loadbalancers.LoadBalancer(
    "nginx_lb_par_2",
    ip_ids=[nginx_ip_par_2.id],
    type="LB-S",
    private_networks=[
        {
            "private_network_id": par_2_pn.id,
        }
    ],
    zone=ZONE,
    opts=OPTS,
)

par_2_cluster = scw.kubernetes.Cluster(
    "par_2_cluster",
    name="par-2-cluster",
    version="1.32.3",
    type="kapsule-dedicated-4",
    cni="cilium",
    private_network_id=par_2_pn.id,
    delete_additional_resources=False,
    region=REGION,
    opts=OPTS,
)

par_2_l4_pool = scw.kubernetes.Pool(
    "par_2_l4_pool",
    cluster_id=par_2_cluster.id,
    name="par-2-l4-pool",
    node_type="L4-1-24G",
    size=1,
    autoscaling=True,
    autohealing=True,
    min_size=1,
    max_size=3,
    region=REGION,
    zone=ZONE,
    opts=OPTS,
)
