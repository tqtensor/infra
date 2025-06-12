import pulumi_azure_native as az

# directory: seanquickqr.onmicrosoft.com
az_quickqr_malaysia = az.Provider(
    "az_malaysia",
    subscription_id="75ff1a89-dff8-49f0-a400-b9624f611f16",
    location="malaysiawest",
)
az_quickqr_sweden = az.Provider(
    "az_sweden",
    subscription_id="75ff1a89-dff8-49f0-a400-b9624f611f16",
    location="swedencentral",
)
