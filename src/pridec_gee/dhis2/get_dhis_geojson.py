import requests
from requests.auth import HTTPBasicAuth

def get_dhis_geojson(
    parent_ou: str,
    ou_level: int,
    dhis_url: str,
    dhis_user: str | None = None,
    dhis_pwd: str | None = None,
    dhis_token: str | None = None,
):
    """Retrieve organisation unit GeoJSON from a DHIS2 instance.

    Sends a GET request to the DHIS2 GeoJSON API endpoint to retrieve
    organisation units at a specified level under a parent organisation unit.

    Args:
        parent_ou: UID of the parent organisation unit.
        ou_level: Organisation unit hierarchy level to retrieve.
        dhis_url: Base URL of the DHIS2 instance.
        dhis_user: Username for the DHIS2 instance. Required if
            `dhis_token` is not provided.
        dhis_pwd: Password for the DHIS2 instance. Required if
            `dhis_token` is not provided.
        dhis_token: Personal access token for the DHIS2 instance.
            Can be provided instead of `dhis_user` and `dhis_pwd`.

    Returns:
        dict: GeoJSON FeatureCollection of organisation units.
    """

    if not dhis_token and not (dhis_user and dhis_pwd):
        raise ValueError("Authentication required: provide either a token or both user and pwd")

    # Authentication setup
    headers = {'Authorization': f'ApiToken {dhis_token}'} if dhis_token else {}
    auth = None if dhis_token else HTTPBasicAuth(dhis_user, dhis_pwd)
    geo_url = f"{dhis_url.rstrip('/')}/api/organisationUnits.geojson?parent={parent_ou}&level={ou_level}&fields=id,geometry"

    response = requests.get(geo_url, headers = headers, auth = auth)
    response.raise_for_status()
    geojson = response.json()

    features = []

    for feature in geojson.get("features", []):
        geom = feature.get("geometry")

        if not geom:
            continue

        if geom.get("type") not in {"Polygon", "MultiPolygon"}:
            continue

        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "orgUnit": feature.get("id")
            }
        })

    org_units = {
        "type": "FeatureCollection",
        "features": features
    }

    return org_units