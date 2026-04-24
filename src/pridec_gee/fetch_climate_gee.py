import ee
import logging
import pandas as pd

from .gee.fetch_fewsnet_windspeed import fetch_fewsnet_windspeed
from .gee.fetch_era5_climate import fetch_era5_climate
from .gee.fetch_modis_aod import fetch_modis_aod
from .gee.fetch_modis_fire import fetch_modis_fire
from .gee.fetch_sen1_flood import fetch_sen1_flood
from .gee.fetch_sen2_indicators import fetch_sen2_indicators
from .dhis2.get_dhis_geojson import get_dhis_geojson
from .dhis2.post_climate import post_climate
from .gee.variables import AVAILABLE_VARIABLES, FEWSNET_VARIABLES, SEN2_VARIABLES, ERA5_VARIABLES
from .gee.utils import validate_variables

logger = logging.getLogger(__name__)

def fetch_climate_gee(
    date_range: dict[str, str],
    orgUnit: ee.FeatureCollection,
    variables: list[str] = AVAILABLE_VARIABLES,
    rice_features: ee.FeatureCollection = None
):
    """
    Process PRIDE-C climate variables on a GEE server and download locally

    Args:
        orgUnit: FeatureCollection of orgUnits to download.
        date_range: Dictionary with keys 'start_date_gee' and 'end_date_gee'
            representing the date range to download. Date format is YYYY-MM-DD
        variables: List of variables to import. See ``AVAILABLE VARIABLES`` for full list. Defaults to all
        rice_features: FeatureCollection of rice fields if download `pridec_climate_floodedRice` data.

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

    validate_variables(input_vars = variables, allowed_vars = AVAILABLE_VARIABLES)

    logger.info("Processing and downloading the following variables from GEE: %s", variables)

    all_vars = []

    if set(FEWSNET_VARIABLES) & set(variables):
        logger.info("Downloading FEWSNET variables: %s", set(FEWSNET_VARIABLES) & set(variables))
        fewsnet_df = fetch_fewsnet_windspeed(orgUnit, date_range)
        all_vars.append(fewsnet_df)

    if set(ERA5_VARIABLES) & set(variables):
        logger.info("Downloading ERA5 climate variables: %s", set(ERA5_VARIABLES) & set(variables))
        era5_df = fetch_era5_climate(orgUnit, date_range)
        all_vars.append(era5_df)
    
    if "pridec_climate_AOD" in variables:
        logger.info("Downloading pridec_climate_AOD")
        aod_df = fetch_modis_aod(orgUnit, date_range)
        all_vars.append(aod_df)

    if "pridec_climate_propFire" in variables:
        logger.info("Downloading pridec_climate_propFire")
        fire_df = fetch_modis_fire(orgUnit, date_range)
        all_vars.append(fire_df)

    if set(SEN2_VARIABLES) & set(variables):
        logger.info("Downloading Sen2 Vegetation Indicators: %s", set(SEN2_VARIABLES) & set(variables))
        sen2_df = fetch_sen2_indicators(orgUnit, date_range)
        all_vars.append(sen2_df)
    
    if "pridec_climate_floodedRice" in variables:
        if rice_features is None:
            logger.error("Argument ``rice_features`` must be provided to estimate Sen-1 Ricefield flooding dynamics")
            return
        
        logger.info("Downloading pridec_climate_floodedRice. This can take 30-45 minutes depending on the date range")

        flood_df = fetch_sen1_flood(rice_features, date_range)
        all_vars.append(flood_df)

    #combine into one large dataframe to return
    combined_df = pd.concat(all_vars, ignore_index=True)

    return(combined_df)

