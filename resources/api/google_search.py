import pulumi
import pulumi_gcp as gcp

from resources.providers import gcp_pixelml_eu_west_4
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml", region="eu-west-4", type="resource", provider="gcp"
)


required_services = [
    "apikeys.googleapis.com",
    "customsearch.googleapis.com",
]

enabled_services = {}
for i, service in enumerate(required_services):
    enabled_services[service] = gcp.projects.Service(
        f"enable-{service}",
        project=gcp_pixelml_eu_west_4.project,
        service=service,
        disable_dependent_services=True,
        opts=OPTS,
    )

google_search_api_key = gcp.projects.ApiKey(
    "google_search_api_key",
    name="search-api-key",
    display_name="Search API Key",
    restrictions={"api_targets": [{"service": "customsearch.googleapis.com"}]},
    project=gcp_pixelml_eu_west_4.project,
    opts=get_options(
        profile="pixelml",
        region="eu-west-4",
        type="resource",
        provider="gcp",
        kwargs={"depends_on": list(enabled_services.values())},
    ),
)

pulumi.export("API: google_search_api_key", google_search_api_key.key_string)
