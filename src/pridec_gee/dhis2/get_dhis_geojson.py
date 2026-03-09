import requests
from requests.auth import HTTPBasicAuth

def get_dhis_geojson(parent_ou, ou_level, dhis_url, dhis_user=None, dhis_pwd=None, dhis_token=None):
    """
    GETs geojson of orgUnits from DHIS2 instance
    
    Args:
        parent_ou (string): id of parent orgUnit
        ou_level (int): hierarchy level of OrgUnit
        dhis_url (string): base url of DHIS2 instance
        dhis_user (str, optional) :   username for dhis2 instance
        dhis_pwd (str, optional)  :   password for dhis2 instance
        dhis_token (str, optional):   personal access token for dhis2 instance.
                                 Can be provided instead of user and pwd.

    Returns:
        FeatureCollection: geojson of orgUnits
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