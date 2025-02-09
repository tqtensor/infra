import pulumi_kubernetes as k8s

from .aws import *  # noqa
from .gcp import *  # noqa

k8s_provider = k8s.Provider("k8s-provider")
