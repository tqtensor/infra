from resources.constants import netherlands_ts_external_ip

whitelist_cidrs = [
    netherlands_ts_external_ip.address.apply(lambda ip: f"{ip}/32"),
]
