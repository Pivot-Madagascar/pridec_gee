import ee
import pandas as pd

from .utils import month_agg_sp_mean, add_tempC, add_rh, add_dewtempC

def fetch_era5_climate(
    orgUnit: ee.FeatureCollection,
    date_range: dict[str, str],
):
    """Extract temperature, precipitation, and relative humidity from ERA5 data.

    Retrieves monthly climate variables for the specified orgUnits from GEE.
    Outputs a JSON-ready list formatted for DHIS2 import.

    Args:
        orgUnit: FeatureCollection of orgUnit polygons to extract data from.
        date_range: Dictionary containing start and end dates with keys:
            - 'start_date_gee': YYYY-MM-DD string of start date
            - 'end_date_gee': YYYY-MM-DD string of end date

    Returns:
        list of dict: Each dict represents a climate measurement with fields:
            - 'orgUnit': organization unit ID
            - 'period': period of observation (YYYYMM)
            - 'value': climate value (e.g., temperature, precipitation)
            - 'dataElement': corresponding DHIS2 data element code
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