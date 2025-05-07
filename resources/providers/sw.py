import pulumi
import pulumiverse_scaleway as sw

config = pulumi.Config("scaleway")
access_key = config.require_secret("access_key")
secret_key = config.require_secret("secret_key")
organization_id = config.require("organization_id")
project_id = config.require("project_id")

sw_pixelml_ams_1 = sw.Provider(
    "sw_pixelml_ams_1",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="nl-ams-1",
)

sw_pixelml_ams_2 = sw.Provider(
    "sw_pixelml_ams_2",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="nl-ams-2",
)

sw_pixelml_ams_3 = sw.Provider(
    "sw_pixelml_ams_3",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="nl-ams-3",
)

sw_pixelml_par_1 = sw.Provider(
    "sw_pixelml_par_1",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="fr-par-1",
)

sw_pixelml_par_2 = sw.Provider(
    "sw_pixelml_par_2",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="fr-par-2",
)

sw_pixelml_par_3 = sw.Provider(
    "sw_pixelml_par_3",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="fr-par-3",
)

sw_pixelml_waw_1 = sw.Provider(
    "sw_pixelml_waw_1",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="pl-waw-1",
)

sw_pixelml_waw_2 = sw.Provider(
    "sw_pixelml_waw_2",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="pl-waw-2",
)

sw_pixelml_waw_3 = sw.Provider(
    "sw_pixelml_waw_3",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="pl-waw-3",
)
