import os
from pathlib import Path

import pandas as pd
import pulumi_cloudflare as cloudflare

from resources.constants import tqtensor_com
from resources.utils import get_options, normalize_email
from resources.vm import nginx_ip_europe_west_4

OPTS = get_options(provider="cloudflare", protect=False)


def create_record(username: str):
    return cloudflare.Record(
        f"{username}_tqtensor_com",
        name=username,
        ttl=1,
        type="A",
        content=nginx_ip_europe_west_4.address,
        zone_id=tqtensor_com.id,
        proxied=True,
        opts=OPTS,
    )


# AWS Workshop
participants = [
    normalize_email(email=email)
    for email in pd.read_csv(
        os.path.join(
            Path(__file__).parent.parent.parent.parent, "artifacts", "participants.csv"
        )
    )["email"].values
]

for participant in participants:
    username = participant.split("@")[0]
    exec(f"{username}_tqtensor_com = create_record(username=username)")
