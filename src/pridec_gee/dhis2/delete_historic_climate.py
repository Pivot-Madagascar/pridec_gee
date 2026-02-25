import requests
from requests.auth import HTTPBasicAuth
import json
import os
import pandas as pd

from dateutil.relativedelta import relativedelta

def delete_historic_climate(base_url, dataElement, delete_months, orgUnit_ids, user=None, pwd=None, token=None, dryRun=False):
    """
    Deletes dataElement values from past delete_months months

    Args:
        base_url (str)           url of dhis2 instance
        dataElement (str)        code of dataElement to delete
        delete_months (int)      how many months of past data to delete
        orgUnit_ids (list)       list of orgUnit ids to delete data from
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
    
    #create json of full range to delete
    today = pd.Timestamp.today().normalize()
    end_date = today.replace(day=1)
    start_date = end_date - relativedelta(months = delete_months)

    df_periods = pd.DataFrame({'period': pd.date_range(start = start_date, end = end_date, freq = 'MS')})
    df_periods['period'] = df_periods['period'].dt.strftime('%Y%m')
    df_orgUnit = pd.DataFrame({'orgUnit': orgUnit_ids})

    full_range = df_periods.merge(df_orgUnit, how = 'cross')
    full_range['dataElement'] = dataElement
    full_range['value'] = 9999

    delete_json = {"dataValues": full_range.to_dict(orient='records')}

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
    response = requests.post(url, headers=headers, auth=auth, json=delete_json)

    # resp.json().get("httpStatus")
    # resp.json().get("status")
    # resp.json().get("message")
    # resp_text = response.json().get("response") #for debugging

    return response