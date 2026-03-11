import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime

from dateutil.relativedelta import relativedelta

def delete_historic_climate(
    base_url: str,
    dataElement: str,
    delete_month_range: list[str],
    orgUnit_ids: list[str],
    user: str | None = None,
    pwd: str | None = None,
    token: str | None = None,
    dryRun: bool = False,
) -> requests.Response:
    """Delete historic climate data values from a DHIS2 instance.

    Deletes values for a specified climate data element across a given
    range of months and a list of organisation units.

    Args:
        base_url: URL of the DHIS2 instance.
        dataElement: Code of the data element to delete
            (e.g., "pridec_climate_AOD").
        delete_month_range: Start and end months for deletion in YYYYMM
            format (e.g., ["202201", "202208"]).
        orgUnit_ids: List of organisation unit UIDs to delete data from.
        user: Username for the DHIS2 instance. Required if `token`
            is not provided.
        pwd: Password for the DHIS2 instance. Required if `token`
            is not provided.
        token: Personal access token for the DHIS2 instance. Can be
            provided instead of `user` and `pwd`.
        dryRun: If True, perform a dry run of the deletion request.
            If False, execute the deletion.

    Returns:
        requests.Response: Response object returned by the DHIS2 POST request.
    """
    if not token and not (user and pwd):
        raise ValueError("Authentication required: provide either a token or both user and pwd")
    
    if dryRun:
        print("Running in dryRun mode. No data will be deleted.")

    
    #create json of full range to delete
    start_date = datetime.strptime(delete_month_range[0], "%Y%m")
    end_date = datetime.strptime(delete_month_range[1], "%Y%m")

    df_periods = pd.DataFrame({'period': pd.date_range(start = start_date, end = end_date, freq = 'MS')})
    df_periods['period'] = df_periods['period'].dt.strftime('%Y%m')
    df_orgUnit = pd.DataFrame({'orgUnit': orgUnit_ids})

    full_range = df_periods.merge(df_orgUnit, how = 'cross')
    full_range['dataElement'] = dataElement
    full_range['value'] = 9999

    delete_json = {"dataValues": full_range.to_dict(orient='records')}

    endpoint = (
        "/api/dataValueSets"
        f"?dryRun={'true' if dryRun else 'false'}"
        "&dataElementIdScheme=code"
        "&orgUnitIdScheme=uid"
        "&categoryOptionComboIdScheme=code"
        "&idScheme=code"
        "&importStrategy=DELETE"
        "&force=true"
    )


    url = f"{base_url.rstrip('/')}{endpoint}"

    # Authentication setup
    headers = {'Authorization': f'ApiToken {token}'} if token else {}
    auth = None if token else HTTPBasicAuth(user, pwd)
    
    if dryRun is False:
        print("You are not in dryRun mode. This will delete data on your instance.")
        validate_delete = input("Confirm that you want to continue (yes/no):")
        if validate_delete != "yes":
            print("Exiting process without deleting...")
            return


    #send request
    response = requests.post(url, headers=headers, auth=auth, json=delete_json)

    # resp.json().get("httpStatus")
    # resp.json().get("status")
    # resp.json().get("message")
    # resp_text = response.json().get("response") #for debugging

    return response