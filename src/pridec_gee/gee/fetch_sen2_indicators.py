import ee
import pandas as pd
from numpy import nan as np_nan

from .utils import month_agg_sp_mean, mask_s2_clouds, add_evi, add_gao, add_mndwi

def fetch_sen2_indicators(orgUnit, date_range):
    """
    Extract EVI, MNDWI, and NDWI GAO at monthly frequency from Sentinel-2 data to match orgUnit

    Args:
        orgUnit (ee.FeatureCollection):     orgUnit polygons to use for extraction. If None, will get from DHIS2 instance
        date_range (list):                   range of dates to download data of. 
                                                Format is a string (start_date_gee[%Y-%m-%d], end_date_gee[%Y-%m-%d]) 

    Returns:
        JSON file with columns orgUnit, period, value, dataElement formatted to submit to DHIS2
    """

    date_seq = pd.date_range(start = pd.to_datetime(date_range['start_date_gee']), 
                             end = pd.to_datetime(date_range['end_date_gee']), freq = 'MS')
    
    month_group = date_seq.to_series().groupby(date_seq.year)

    ic = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(orgUnit) \
    .map(mask_s2_clouds).map(add_evi).map(add_gao).map(add_mndwi)

    fxparams = {
    'reducer': ee.Reducer.mean(), 
    'bands': ['EVI', 'GAO', 'MNDWI'],  
    'bandsRename': ['pridec_climate_evi', 'pridec_climate_gao', 'pridec_climate_mndwi']  
    }
    #because of the 5000 call limit, we loop by year
    df_all_years = []
    for year, months in month_group:
        this_start = months.min().strftime('%Y-%m-%d')
        this_end = months.max().strftime('%Y-%m-%d')

        result = month_agg_sp_mean(ic, orgUnit, this_start, this_end, fxparams)
        df_all_years.append(pd.DataFrame(result))
    
    df = pd.concat(df_all_years, ignore_index=True)

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