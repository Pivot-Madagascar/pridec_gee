import requests
from requests.auth import HTTPBasicAuth

def get_dhis_geojson(PARENT_OU, OU_LEVEL, dhis_url, dhis_user=None, dhis_pwd=None, dhis_token=None):
    """
    GETs geojson of orgUnits from DHIS2 instance
    
    Args:
        PARENT_OU (string): id of parent orgUnit
        OU_LEVEL (int): hierarchy level of OrgUnit
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
    geo_url = f"{dhis_url}api/organisationUnits.geojson?parent={PARENT_OU}&level={OU_LEVEL}"

    response = requests.get(geo_url, headers = headers, auth = auth)
    response.raise_for_status()
    geojson = response.json()

    org_units = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": feature["geometry"],
                "properties": {
                    "orgUnit": feature["id"]
                }
            }
            for feature in geojson["features"]
            if "geometry" in feature and feature["geometry"]
        ]
        }
    return org_units