import requests
from requests.auth import HTTPBasicAuth

def get_pridec_elements(
    dhis_url: str,
    dhis_user: str  = None,
    dhis_pwd: str  = None,
    dhis_token: str = None,
):
    """Retrieve PRIDE-C climate data elements from a DHIS2 instance.

    Sends a GET request to retrieve all data elements associated with the
    PRIDE-C climate dataset, returning their name, code, and ID.

    Args:
        dhis_url: Base URL of the DHIS2 instance.
        dhis_user: Username for the DHIS2 instance. Required if
            `dhis_token` is not provided.
        dhis_pwd: Password for the DHIS2 instance. Required if
            `dhis_token` is not provided.
        dhis_token: Personal access token for the DHIS2 instance.
            Can be provided instead of `dhis_user` and `dhis_pwd`.

    Returns:
        list of dict: Each dict represents a climate data element with keys
        `name`, `code`, and `id`.
    """

    if not dhis_token and not (dhis_user and dhis_pwd):
        raise ValueError("Authentication required: provide either a token or both user and pwd")

    # Authentication setup
    headers = {'Authorization': f'ApiToken {dhis_token}'} if dhis_token else {}
    auth = None if dhis_token else HTTPBasicAuth(dhis_user, dhis_pwd)

    url =  (
        f"{dhis_url.rstrip('/')}/api/dataElements"
        f"?filter=code:like:pridec_climate"
        f"&fields=id,code,displayName,description"
        f"&paging=false"
    )


    response = requests.get(url, headers=headers, auth=auth, timeout=10)
    response.raise_for_status()
    
    de_info = response.json().get('dataElements')
    #pd.json_normalize(de_info).sort_values(by = 'code') #for nice pandas DataFrame
    return de_info


