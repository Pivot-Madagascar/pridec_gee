import ee
import pandas as pd

from .utils import month_agg_sp_mean, add_tempC, add_rh, add_dewtempC

def fetch_era5_climate(orgUnit, date_range):
    """
    Extract temperature, precipitation, and relative humidity from ERA5 data at monthly frequency

    Args:
        orgUnit (ee.FeatureCollection): orgUnit polygons to use for extraction. If None, will get from DHIS2 instance
                        date_range      range of dates to download data of. 
                                            Format is a string (start_date_gee[%Y-%m-%d], end_date_gee[%Y-%m-%d])  

    Returns:
        JSON file with columns orgUnit, period, value, dataElement formatted to submit to DHIS2
    """


    ic = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterBounds(orgUnit) \
    .map(add_tempC).map(add_dewtempC).map(add_rh)

    fxparams = {
    'reducer': ee.Reducer.mean(),  
    'bands': ['temp_c', 'total_precipitation_sum', 'RH'],  
    'bandsRename': ["pridec_climate_temperatureMean", "pridec_climate_precipitation", "pridec_climate_relHumidity"]  
    }

    result = month_agg_sp_mean(ic, orgUnit, date_range['start_date_gee'], date_range['end_date_gee'], fxparams)

    #reformat for DHIS2
    df = pd.DataFrame(result)
    #renaame to PRIDE-C dhis2 code
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