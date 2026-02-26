import requests
from requests.auth import HTTPBasicAuth

def get_pridec_elements(dhis_url, dhis_user=None, dhis_pwd=None, dhis_token=None):
    """
    GETs name, code, and id of PRIDE-C climate dataElements on an instance
    
    Args:
        PARENT_OU (string): id of parent orgUnit
        OU_LEVEL (int): hierarchy level of OrgUnit
        dhis_url (string): base url of DHIS2 instance
        dhis_user (str, optional) :   username for dhis2 instance
        dhis_pwd (str, optional)  :   password for dhis2 instance
        dhis_token (str, optional):   personal access token for dhis2 instance.
                                 Can be provided instead of user and pwd.

    Returns:
        list of climate dataElements associated with PRIDE-C on the instance
    """

    #test/debugging
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    dhis_url = os.environ.get("DHIS2_URL")
    dhis_token = os.getenv("DHIS2_TOKEN")

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
    resp = requests.get(url, headers=headers, auth=auth)
    de_info = resp.json().get('dataElements')
    #pd.json_normalize(de_info).sort_values(by = 'code') #for nice pandas DataFrame
    
    return de_info

