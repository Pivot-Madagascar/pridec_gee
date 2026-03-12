import requests
from requests.auth import HTTPBasicAuth

def post_climate(
    base_url: str,
    payload: dict,
    user: str | None = None,
    pwd: str | None = None,
    token: str | None = None,
    dryRun: bool = False,
):
    """Post climate dataElement values to a DHIS2 instance.

    Can be used for climate data or any other dataElement. Sends a POST
    request with the provided payload to the DHIS2 API.

    Args:
        base_url: URL of the DHIS2 instance.
        payload: JSON payload of dataElement values to send. Typically the
            output of `fetch_*` functions.
        user: Username for the DHIS2 instance. Required if `token` is not provided.
        pwd: Password for the DHIS2 instance. Required if `token` is not provided.
        token: Personal access token for the DHIS2 instance. Can be provided
            instead of `user` and `pwd`.
        dryRun: If True, performs a dry run without actually posting data.
            If False, executes the POST request.

    Returns:
        requests.Response: Response object returned by the DHIS2 POST request.
    """
    if not token and not (user and pwd):
        raise ValueError("Authentication required: provide either a token or both user and pwd")

    endpoint = (
        "/api/dataValueSets"
        f"?dryRun={'true' if dryRun else 'false'}"
        "&dataElementIdScheme=code"
        "&orgUnitIdScheme=uid"
        "&categoryOptionComboIdScheme=code"
        "&idScheme=code"
        "&importStrategy=CREATE_AND_UPDATE"
    )


    url = f"{base_url.rstrip('/')}{endpoint}"

    # Authentication setup
    headers = {'Authorization': f'ApiToken {token}'} if token else {}
    auth = None if token else HTTPBasicAuth(user, pwd)
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)

    return response