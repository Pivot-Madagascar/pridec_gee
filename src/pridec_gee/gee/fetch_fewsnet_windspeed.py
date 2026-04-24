import ee
import pandas as pd


from .utils import month_agg_sp_mean, validate_variables
from .calc_date_range import enforce_two_month_lag

FEWSNET_VARIABLES = ["pridec_climate_windspeed"]

def fetch_fewsnet_windspeed(
    orgUnit: ee.FeatureCollection,
    date_range: dict[str, str],
    variables: list[str] = FEWSNET_VARIABLES
):
    """Extract windspeed from FEWSNET data.

    Retrieves monthly climate variables for the specified orgUnits from GEE.
    Outputs a JSON-ready list formatted for DHIS2 import.

    Args:
        orgUnit: FeatureCollection of orgUnit polygons to extract data from.
        date_range: Dictionary containing start and end dates with keys:
            - 'start_date_gee': YYYY-MM-DD string of start date
            - 'end_date_gee': YYYY-MM-DD string of end date
        variables: variables to be extracted, based on DHIS2 code 
            Options: ["pridec_climate_windspeed"]. Default is all.

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
                       allowed_vars= FEWSNET_VARIABLES)

    ic = ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001").filterBounds(orgUnit)

    #FEWSNET data has a two month latency
    date_range = enforce_two_month_lag(date_range)

    fxparams = {
    'reducer': ee.Reducer.mean(),  
    'bands': ['Wind_f_tavg'],  
    'bandsRename': ["pridec_climate_windspeed"] 
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

    #subset based on variable selection
    df_long = df_long[df_long['dataElement'].isin(variables)]
    df_long = df_long.reset_index(drop=True)

    #turn into a json file
    # df_dict = {
    #     "dataValues": df_long.to_dict(orient="records")
    # }

    return df_long