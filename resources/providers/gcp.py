import pulumi_gcp as gcp

# gen-lang-client-0608717027 account
gcp_pixelml_asia_southeast_1 = gcp.Provider(
    "gcp_pixelml_asia_southeast_1",
    region="asia-southeast1",
    project="gen-lang-client-0608717027",
)
gcp_pixelml_europe_central_2 = gcp.Provider(
    "gcp_pixelml_europe_central_2",
    region="europe-central2",
    project="gen-lang-client-0608717027",
)
gcp_pixelml_us_east_1 = gcp.Provider(
    "gcp_pixelml_us_east_1", region="us-east1", project="gen-lang-client-0608717027"
)
