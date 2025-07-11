import ee
import pandas as pd
import geemap
import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta


from utils.get_dhis_geojson import get_dhis_geojson
from utils.gee_utils import zonal_stats, month_agg_sp_mean
from utils.get_date_range import get_date_range
import os

def fetch_fewsnet_windSpeed(DHIS_TOKEN=None, DHIS_URL=None, PARENT_OU=None, OU_LEVEL=None, orgUnit=None):
    """
    Returns json of windspeed from fewsnet data

    Args:
        DHIS_TOKEN (string, optional) : personal access token for DHIS instance
        DHIS_URL (string, optional) : base url of DHIS for APIs
        PARENT_OU (string, optional) : id of orgUnit that contains the geojsons to extract for
        OU_LEVEL (string,  optional) : hierarchical orgUnit level for the geojson to extract for
        orgUnit (ee.FeatureCollection, optional) orgUnit polygons to use for extractoin. If None, will get from DHIS2 instance

    Returns:
        something
    """
    #get orgUnits from DHIS2 if not provided
    if orgUnit is None:
        org_units = get_dhis_geojson(PARENT_OU=PARENT_OU, OU_LEVEL=OU_LEVEL, DHIS_TOKEN=DHIS_TOKEN, DHIS_URL=DHIS_URL)
        orgUnit = ee.FeatureCollection(org_units)

    date_range =  get_date_range(end_months_ago = 2,
                             end_on_last_day=False)

    ic = ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001").filterBounds(orgUnit).filterDate("2010-01-01", datetime.today())

    fxparams = {
    'reducer': ee.Reducer.mean(),  # Change the reducer if needed
    'bands': ['Wind_f_tavg'],  # Example bands
    'bandsRename': ["pridec_climate_windSpeed"]  # Rename bands
    }

    result = month_agg_sp_mean(ic, orgUnit, date_range['start_date_gee'], date_range['end_date_gee'], fxparams)

    #reformat for DHIS2
    df = pd.DataFrame(result)
    #renaame to PRDIE-C dhis2 code
    df = df.rename(columns={'mean': 'pridec_climate_windSpeed'})

    df_long = df.melt(
        id_vars=['orgUnit', 'period'],
        var_name='dataElement',
        value_name='value'
    )
    #drop missing, round, and change period to string
    df_long = df_long.dropna(subset=['value'])
    df_long['value'] = df_long['value'].round(4)
    df_long['period'] = df_long['period'].astype(str)

    #turn into a json file
    df_dict = {
        "dataValues": df_long.to_dict(orient="records")
    }

    data_json = json.dumps(df_dict, indent=2)

    return data_json