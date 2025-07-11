import ee
import pandas as pd
import geemap
import json
import requests
from datetime import datetime
from numpy import nan as np_nan


from utils.get_dhis_geojson import get_dhis_geojson
from utils.gee_utils import month_agg_sp_mean, mask_s2_clouds, add_evi, add_gao, add_mndwi
from utils.get_date_range import get_date_range
import os

def fetch_sen2_climate(dhis_token=None, dhis_url=None, PARENT_OU=None, OU_LEVEL=None, orgUnit=None):
    """
    Extract EVI, MDNWI, and NDWI GAO at monthly frequency from Sentinel-2 data
    Args:
        dhis_token (string,optional) : personal access token for DHIS instance
        dhis_url (string) : base url of DHIS for APIs
        PARENT_OU (string) : id of orgUnit that contains the geojsons to extract for
        OU_LEVEL (string) : hierarchical orgUnit level for the geojson to extract for
        orgUnit (ee.FeatureCollection, optional) orgUnit polygons to use for extraction. If None, will get from DHIS2 instance

    Returns:
        json of climate data formatted for DHIS2 as dataValues
    """
     #get orgUnits from DHIS2 if not provided
    if orgUnit is None:
        org_units = get_dhis_geojson(PARENT_OU=PARENT_OU, OU_LEVEL=OU_LEVEL, dhis_token=dhis_token, dhis_url=dhis_url)
        orgUnit = ee.FeatureCollection(org_units)

    date_range =  get_date_range(end_months_ago = 1, end_on_last_day=False, start_months_ago =3)

    ic = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterBounds(orgUnit).filterDate("2010-01-01", datetime.today()) \
    .map(mask_s2_clouds).map(add_evi).map(add_gao). map(add_mndwi)

    fxparams = {
    'reducer': ee.Reducer.mean(),  # Change the reducer if needed
    'bands': ['EVI', 'MNDWI', 'GAO'],  # Example bands
    'bandsRename': ['pridec_climate_evi', 'pridec_climate_mndwi', 'pridec_climate_gao']  # Rename bands
    }

    result = month_agg_sp_mean(ic, orgUnit, date_range['start_date_gee'], date_range['end_date_gee'], fxparams)

    #reformat for DHIS2
    df = pd.DataFrame(result)
    #drop mean from column names
    df.columns = [col.removesuffix('_mean') if col.endswith('_mean') else col for col in df.columns]

    df_long = df.melt(
        id_vars=['orgUnit', 'period'],
        var_name='dataElement',
        value_name='value'
    )

    #values outisde of -1 to 1 become NA
    df_long["value"] = df_long["value"].where(df_long["value"].between(-1, 1), np_nan)
    #drop missing, round, and change period to string
    df_long = df_long.dropna(subset=['value'])
    df_long['value'] = df_long['value'].round(4)
    df_long['period'] = df_long['period'].astype(str)

    #turn into a json file
    df_dict = {
        "dataValues": df_long.to_dict(orient="records")
    }

    return df_dict