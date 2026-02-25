import requests
from requests.auth import HTTPBasicAuth
import json
import os

def delete_dataValues(base_url, payload, user=None, pwd=None, token=None, dryRun=False):
    """
    Deletes dataElement values within a DHIS2 instance

    Args:
        base_url (str)           url of dhis2 isntance
        payload (dict)           JSON payload containing dataElements, orgUnits, and period to delete. All values should be set to 9999.
        user (str, optional)     username for dhis2 instance
        pwd (str, optional)      password for dhis2 instance
        token (str, optional)    personal access token for dhis2 instance.
                                 Can be provided instead of user and pwd.
        dryRun (boolean)         True: test a dry run of the DELETE
                                 False: actually DELETE the data
    
    Returns:
        requests.Response: Response object from DELETE request
    """
    if not token and not (user and pwd):
        raise ValueError("Authentication required: provide either a token or both user and pwd")

    endpoint = (
        "api/dataValueSets"
        f"?dryRun={'true' if dryRun else 'false'}"
        "&dataElementIdScheme=code"
        "&orgUnitIdScheme=uid"
        "&categoryOptionComboIdScheme=code"
        "&idScheme=code"
        "&importStrategy=DELETE"
        "&force=true"
    )


    url = f"{base_url.rstrip('/')}/{endpoint}"

    # Authentication setup
    headers = {'Authorization': f'ApiToken {token}'} if token else {}
    auth = None if token else HTTPBasicAuth(user, pwd)
    
    #send request
    response = requests.post(url, headers=headers, auth=auth, json=payload)

    # resp.json().get("httpStatus")
    # resp.json().get("status")
    # resp.json().get("message")
    # resp_text = response.json().get("response") #for debugging

    return response