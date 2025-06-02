import pulumi
import pulumiverse_scaleway as scw

config = pulumi.Config("scaleway")
access_key = config.require_secret("access_key")
secret_key = config.require_secret("secret_key")
organization_id = config.require("organization_id")
project_id = config.require("project_id")

scw_pixelml_ams_1 = scw.Provider(
    "scw_pixelml_ams_1",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="nl-ams-1",
)

scw_pixelml_ams_2 = scw.Provider(
    "scw_pixelml_ams_2",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="nl-ams-2",
)

scw_pixelml_ams_3 = scw.Provider(
    "scw_pixelml_ams_3",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="nl-ams-3",
)

scw_pixelml_par_1 = scw.Provider(
    "scw_pixelml_par_1",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="fr-par-1",
)

scw_pixelml_par_2 = scw.Provider(
    "scw_pixelml_par_2",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="fr-par-2",
)

scw_pixelml_par_3 = scw.Provider(
    "scw_pixelml_par_3",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="fr-par-3",
)

scw_pixelml_waw_1 = scw.Provider(
    "scw_pixelml_waw_1",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="pl-waw-1",
)

scw_pixelml_waw_2 = scw.Provider(
    "scw_pixelml_waw_2",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="pl-waw-2",
)

scw_pixelml_waw_3 = scw.Provider(
    "scw_pixelml_waw_3",
    access_key=access_key,
    secret_key=secret_key,
    organization_id=organization_id,
    project_id=project_id,
    zone="pl-waw-3",
)
