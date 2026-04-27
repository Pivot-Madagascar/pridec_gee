import ee
import pandas as pd

from .utils import month_agg_sp_mean, add_tempC, add_rh, add_dewtempC, validate_variables

ERA5_VARIABLES = ["pridec_climate_temperatureMean", "pridec_climate_precipitation", "pridec_climate_relHumidity"]

def fetch_era5_climate(
    orgUnit: ee.FeatureCollection,
    date_range: dict[str, str],
    variables: list[str] = ERA5_VARIABLES
):
    """Extract temperature, precipitation, and relative humidity from ERA5 data.

    Retrieves monthly climate variables for the specified orgUnits from GEE.
    Outputs a JSON-ready list formatted for DHIS2 import.

    Args:
        orgUnit: FeatureCollection of orgUnit polygons to extract data from.
        date_range: Dictionary containing start and end dates with keys:
            - 'start_date_gee': YYYY-MM-DD string of start date
            - 'end_date_gee': YYYY-MM-DD string of end date
        variables: variables to be extracted, based on DHIS2 code 
            Options: ["pridec_climate_temperatureMean", "pridec_climate_precipitation", "pridec_climate_relHumidity"]. Default is all.

    Returns: 
        pandas dataframe with columns:
            - 'orgUnit': organization unit ID
            - 'period': period of observation (YYYYMM)
            - 'value': climate value (e.g., temperature, precipitation)
            - 'dataElement': corresponding DHIS2 data element code (pridec_climate_*)
        Can be turned into a DHIS2 formatted json file with:
                df_dict = {
                    "dataValues": df_long.to_dict(orient="records")
                }
    """

    validate_variables(input_vars = variables,
                       allowed_vars= ERA5_VARIABLES)

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

    #subset based on variable selection
    df_long = df_long[df_long['dataElement'].isin(variables)]
    df_long = df_long.reset_index(drop=True)

    return df_long