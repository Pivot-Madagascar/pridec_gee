import requests
from requests.auth import HTTPBasicAuth

def post_climate(base_url, payload, user=None, pwd=None, token=None, dryRun=False):
    """
    Posts dataElement values to a dhis2 instance. Meant to be used for climate data, but can be used for any dataElement.

    Args:
        base_url (str)           url of dhis2 isntance
        payload (dict)           JSON payload of climate data to send in POST. Output of fetch_* functions
        user (str, optional)     username for dhis2 instance
        pwd (str, optional)      password for dhis2 instance
        token (str, optional)    personal access token for dhis2 instance.
                                 Can be provided instead of user and pwd.
        dryRun (boolean)         True: test a dry run of the POST
                                 False: actually post the data
    
    Returns:
        requests.Response: Response object from POST request
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
        "&importStrategy=CREATE_AND_UPDATE"
    )


    url = f"{base_url.rstrip('/')}/{endpoint}"

    # Authentication setup
    headers = {'Authorization': f'ApiToken {token}'} if token else {}
    auth = None if token else HTTPBasicAuth(user, pwd)
    
    #send request
    response = requests.post(url, headers=headers, auth=auth, json=payload)

    # def clean_json_resp(resp):
    #     try:
    #         resp.json()
    #     except:
    #         "Empty API Response"
    
    # resp_text = clean_json_resp(response)

    # resp.json().get("httpStatus")
    # resp.json().get("status")
    # resp.json().get("message")
    # resp_text = response.json().get("response") #for debugging

    return response