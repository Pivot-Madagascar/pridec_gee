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

def fetch_modis_fire(dhis_token=None, dhis_url=None, PARENT_OU=None, OU_LEVEL=None, orgUnit=None):
    """
    Extracts mean Aerosol Optical Depth from MODIS satellite by month for orgUnits from DHIS2

    Args:
        dhis_token (string, optional) : personal access token for DHIS instance
        dhis_url (string, optional) : base url of DHIS for APIs
        PARENT_OU (string, optional) : id of orgUnit that contains the geojsons to extract for
        OU_LEVEL (string, optional) : hierarchical orgUnit level for the geojson to extract for
        orgUnit (ee.FeatureCollection, optional) orgUnit polygons to use for extractoin. If None, will get from DHIS2 instance

    Returns:
        something
    """

    #get orgUnits from DHIS2 if not provided
    if orgUnit is None:
        org_units = get_dhis_geojson(PARENT_OU=PARENT_OU, OU_LEVEL=OU_LEVEL, dhis_token=dhis_token, dhis_url=dhis_url)
        orgUnit = ee.FeatureCollection(org_units)

    date_range =  get_date_range(end_months_ago = 1, end_on_last_day=False)

    ic = ee.ImageCollection("MODIS/061/MYD14A2").filterBounds(orgUnit).filterDate("2015-01-01", datetime.today())
    #defaut parameters from first image
    img_rep = ic.first()
    default_scale = img_rep.select([0]).projection().nominalScale().getInfo()

        # Create list of dates that we would like to loop over
    first_day_date = ee.Date(date_range['start_date_gee'])
    last_day_date = ee.Date(date_range['end_date_gee'])
    n_months = last_day_date.difference(first_day_date, 'month')
    date_list = ee.List.sequence(0, n_months, 1)

    def make_datelist(n):
        return first_day_date.advance(n, 'month')
    dates = date_list.map(make_datelist)

    # Function to get aggregate for each month based on the first day of the month
    def month_func(this_date):
        start_date = ee.Date(this_date)  # starting date
        end_date = start_date.advance(1, 'month')  # end of month for filter
        filter_step = ic.filter(ee.Filter.date(start_date, end_date)) \
                         .select('FireMask')
        
        #get maximum value for each pixel in Firemask during the month
        reduce_step1 = filter_step.reduce(  # Apply reducer
            reducer = ee.Reducer.max()
        )
        #then reclassify to only keep pixels with 7 or greater (low confidence of fire)
        reduce_step2 = reduce_step1.gte(7) \
        .set('system:time_start', start_date.millis()).set('year_month', start_date.format("YYYYMM"))

        return ee.Image(reduce_step2)
    
    # Map over the list of dates and create monthly aggregated image collection
    ic_month = ee.ImageCollection(dates.map(month_func).flatten())

    # Function for calculating spatial mean by region
    def calc_spatial_mean(image):
        # Reduce the image by regions
        reduced = image.reduceRegions(
            collection=orgUnit,
            reducer=ee.Reducer.mean(),  # Spatial mean
            scale=default_scale,
            crs="EPSG:4326"
        )
        
        # Add metadata to each feature
        return reduced.map(lambda f: f.set({
            'period': image.get('year_month')
        }).setGeometry(None))  # Remove geometry to save space
    
    # Apply the spatial mean function to each image in the collection
    results_fc = ic_month.map(calc_spatial_mean).flatten()
    results_list = results_fc.getInfo()
    #to deal with nestedness
    results_data = results_list.get('features', [])
    result = [feature['properties'] for feature in results_data]

    #reformat for DHIS2
    df = pd.DataFrame(result)
    #rename to PRIDE-C dhis2 code
    df = df.rename(columns={'mean': 'pridec_climate_propFire'})

    df_long = df.melt(
        id_vars=['orgUnit', 'period'],
        var_name='dataElement',
        value_name='value'
    )
    #drop missing, round, and change period to string
    df_long = df_long.dropna(subset=['value'])
    df_long['value'] = df_long['value'].round(6)
    df_long['period'] = df_long['period'].astype(str)

    #turn into a json file
    df_dict = {
        "dataValues": df_long.to_dict(orient="records")
    }

    return df_dict