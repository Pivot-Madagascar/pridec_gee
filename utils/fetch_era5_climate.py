import ee
import pandas as pd
import geemap
import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta


from utils.get_dhis_geojson import get_dhis_geojson
from utils.gee_utils import zonal_stats, month_agg_sp_mean, add_tempC, add_rh, add_dewtempC
from utils.get_date_range import get_date_range
import os

def fetch_era5_climate(dhis_token=None, dhis_url=None, PARENT_OU=None, OU_LEVEL=None, orgUnit=None):
    """
    Extract temperature, precipitation, and relative humidity from ERA5 data at monthly frequency

    Args:
        dhis_token (string, optional) : personal access token for DHIS instance
        dhis_url (string, optional) : base url of DHIS for APIs
        PARENT_OU (string, optional) : id of orgUnit that contains the geojsons to extract for
        OU_LEVEL (string, optional) : hierarchical orgUnit level for the geojson to extract for
        orgUnit (ee.FeatureCollection, optional) orgUnit polygons to use for extraction. If None, will get from DHIS2 instance

    Returns:
        something
    """
    if orgUnit is None:
        org_units = get_dhis_geojson(PARENT_OU=PARENT_OU, OU_LEVEL=OU_LEVEL, dhis_token=dhis_token, dhis_url=dhis_url)
        orgUnit = ee.FeatureCollection(org_units)

    date_range =  get_date_range(end_months_ago = 1, end_on_last_day=False, start_months_ago =3)

    ic = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterBounds(orgUnit).filterDate("2010-01-01", datetime.today()) \
    .map(add_tempC).map(add_dewtempC).map(add_rh)

    fxparams = {
    'reducer': ee.Reducer.mean(),  # Change the reducer if needed
    'bands': ['temp_c', 'total_precipitation_sum', 'RH'],  # Example bands
    'bandsRename': ["pridec_climate_temperatureMean", "pridec_climate_precipitation", "pridec_climate_relHumidity"]  # Rename bands
    }

    result = month_agg_sp_mean(ic, orgUnit, date_range['start_date_gee'], date_range['end_date_gee'], fxparams)

    #reformat for DHIS2
    df = pd.DataFrame(result)
    #renaame to PRDIE-C dhis2 code
    df.columns = [col.removesuffix('_mean') if col.endswith('_mean') else col for col in df.columns]
    #precipitation needs to be in mm
    df['pridec_climate_precipitation'] =  df['pridec_climate_precipitation'] * 1000

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

    return df_dict