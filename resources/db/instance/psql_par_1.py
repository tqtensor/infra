from pathlib import Path

import pulumiverse_scaleway as scw

from resources.utils import fill_in_password, get_options

OPTS = get_options(
    profile="pixelml", provider="scw", region="par-1", type="resource", protect=False
)
REGION = "fr-par"


accounts_file_path = Path(__file__).parent / "accounts.yaml"
account_values = fill_in_password(
    encrypted_yaml=accounts_file_path, value_path="psql_par_1_instance.password"
)

psql_par_1_instance = scw.databases.Instance(
    "psql_par_1_instance",
    name="psql-par-1-instance",
    node_type="DB-DEV-S",
    engine="PostgreSQL-14",
    is_ha_cluster=False,
    disable_backup=False,
    user_name=account_values["psql_par_1_instance"]["username"],
    password=account_values["psql_par_1_instance"]["password"],
    encryption_at_rest=True,
    region=REGION,
    opts=OPTS,
)
