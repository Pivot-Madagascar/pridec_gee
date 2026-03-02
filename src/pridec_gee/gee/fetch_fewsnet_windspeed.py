import ee
import pandas as pd


from .utils import month_agg_sp_mean
from .calc_date_range import enforce_two_month_lag

def fetch_fewsnet_windspeed(orgUnit, date_range):
    """
    Fetch FEWSNET Windspeed data from GEE for specified orgUnits at monthly frequency

        Args:
        orgUnit (ee.FeatureCollection):     orgUnit polygons to use for extraction. If None, will get from DHIS2 instance
        date_range (list)                   range of dates to download data of. 
                                                Format is a string (start_date_gee[%Y-%m-%d], end_date_gee[%Y-%m-%d]) 

    Returns:
        JSON file with columns orgUnit, period, value, dataElement formatted to submit to DHIS2
    """

    ic = ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001").filterBounds(orgUnit)

    #FEWSNET data has a two month latency
    date_range = enforce_two_month_lag(date_range)

    fxparams = {
    'reducer': ee.Reducer.mean(),  
    'bands': ['Wind_f_tavg'],  
    'bandsRename': ["pridec_climate_windSpeed"] 
    }

    result = month_agg_sp_mean(ic, orgUnit, date_range['start_date_gee'], date_range['end_date_gee'], fxparams)

    #reformat for DHIS2
    df = pd.DataFrame(result)
    #renaame to PRDIE-C dhis2 code
    df = df.rename(columns={'mean': 'pridec_climate_windspeed'})

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