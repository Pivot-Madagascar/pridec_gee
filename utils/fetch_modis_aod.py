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

def fetch_modis_aod(dhis_token=None, dhis_url=None, PARENT_OU=None, OU_LEVEL=None, orgUnit=None, historical_months=3):
    """
    Extracts mean Aerosol Optical Depth from MODIS satellite by month for orgUnits from DHIS2

    Args:
        dhis_token (string, optional) : personal access token for DHIS instance
        dhis_url (string, optional) : base url of DHIS for APIs
        PARENT_OU (string, optional) : id of orgUnit that contains the geojsons to extract for
        OU_LEVEL (string) : hierarchical orgUnit level for the geojson to extract for
        orgUnit (ee.FeatureCollection, optional) orgUnit polygons to use for extractoin. If None, will get from DHIS2 instance
        historical_months (int, optional): how many prior months of data to import. Default = 3

    Returns:
        json of AOD formatted for DHIS2 instance
    """

    #get orgUnits from DHIS2 if not provided
    if orgUnit is None:
        org_units = get_dhis_geojson(PARENT_OU=PARENT_OU, OU_LEVEL=OU_LEVEL, dhis_token=dhis_token, dhis_url=dhis_url)
        orgUnit = ee.FeatureCollection(org_units)

    date_range =  get_date_range(end_months_ago = 1, end_on_last_day=False, start_months_ago=historical_months)

    ic = ee.ImageCollection("MODIS/061/MCD19A2_GRANULES").filterBounds(orgUnit).filterDate("2015-01-01", datetime.today())
    ic_mask = ic.map(apply_qa_mask) 

    fxparams = {
    'reducer': ee.Reducer.mean(),  # Change the reducer if needed
    'bands': ['Optical_Depth_047',],  # Example bands
    'bandsRename': ['AOD47']  # Rename bands
    }

    result = month_agg_sp_mean(ic_mask, orgUnit, date_range['start_date_gee'], date_range['end_date_gee'], fxparams)

    #reformat for DHIS2
    df = pd.DataFrame(result)
    #rename to PRIDE-C dhis2 code
    df = df.rename(columns={'mean': 'pridec_climate_AOD'})

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

def bitwise_extract(input_value, from_bit, to_bit):
    """
    Extracts bits from a number or image using bitwise operations.

    Args:
        input_value (ee.Number or ee.Image): Input to extract bits from.
        from_bit (int): Starting bit position.
        to_bit (int): Ending bit position.

    Returns:
        ee.Number or ee.Image: The extracted bits.
    """
    mask_size = ee.Number(1).add(to_bit).subtract(from_bit)
    mask = ee.Number(1).leftShift(mask_size).subtract(1)
    return input_value.rightShift(from_bit).bitwiseAnd(mask)

def apply_qa_mask(image):
    """
    Applies a QA bitmask to an AOD image, keeping only pixels with QA <= 4.

    Args:
        image (ee.Image): MODIS AOD image with 'Optical_Depth_047' and 'AOD_QA' bands.

    Returns:
        ee.Image: Masked 'Optical_Depth_047' band.
    """
    aod_depth = image.select('Optical_Depth_047')
    qc_aod = image.select('AOD_QA')
    qa_mask = bitwise_extract(qc_aod, 8, 11).lte(4)
    return aod_depth.updateMask(qa_mask)