import ee
import logging

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
from .fetch_climate_gee import fetch_climate_gee

logger = logging.getLogger(__name__)

def import_pridec_climate(
    dhis_url: str,
    date_range: dict[str, str],
    orgUnit: ee.FeatureCollection = None,
    parent_ou: str = None,
    ou_level: int = None,
    variables: list[str] = AVAILABLE_VARIABLES,
    rice_features: ee.FeatureCollection = None,
    dhis_user: str = None,
    dhis_pwd: str = None,
    dhis_token: str = None,
    dryRun: bool = True,
):
    """
    Import PRIDE-C variables into a DHIS2 instance.

    Args:
        dhis_url: URL of the DHIS2 instance.
        date_range: Dictionary with keys 'start_date_gee' and 'end_date_gee'
            representing the date range to download. Date format is YYYY-MM-DD
        orgUnit: FeatureCollection of orgUnits to download (optional).
        parent_ou: UID of parent orgUnit for GeoJSON download (optional).
        ou_level: Hierarchical level of orgUnit to extract for (optional).
        variables: List of variables to import. See ``AVAILABLE VARIABLES`` for full list. Defaults to all
        rice_features: FeatureCollection of rice fields if importing `pridec_climate_floodedRice` data.
        dhis_user: Username for DHIS2 instance (optional).
        dhis_pwd: Password for DHIS2 instance (optional).
        dhis_token: Personal access token for DHIS2. Can be used instead of `dhis_user`/`dhis_pwd`.
        dryRun: If True, performs a dry run without posting data. Defaults to True.

    Returns:
        requests.Response: Response object from POST request
    """

    validate_variables(input_vars = variables, allowed_vars = AVAILABLE_VARIABLES)
    if "pridec_climate_floodedRice" in variables:
        if rice_features is None:
            logger.error("Argument ``rice_features`` must be provided to import Sen-1 Ricefield flooding dynamics")
            return

    logger.info("Updating PRIDEC Climate variables for URL %s",
                dhis_url)
    logger.info("Variables to import: %s", variables)
    logger.info("Using configuration dryRun = %s", dryRun)



    if orgUnit is None:
        logger.info("Fetching geojson for parent %s at level %s",
                    parent_ou, ou_level)
        org_units = get_dhis_geojson(parent_ou=parent_ou, ou_level=ou_level, 
                                    dhis_token=dhis_token, dhis_user=dhis_user, dhis_pwd=dhis_pwd, dhis_url=dhis_url)
        orgUnit = ee.FeatureCollection(org_units)

    climate_df = fetch_climate_gee(date_range = date_range,
                                   orgUnit = orgUnit,
                                   variables = variables,
                                   rice_features =  rice_features)
    
    climate_json = {
                    "dataValues": climate_df.to_dict(orient="records")
                }
    
    logger.info("Posting climate data to DHIS2 instance %s with dryRun=%s", dhis_url, dryRun)

    resp = post_climate(base_url = dhis_url, payload = climate_json, 
                            token = dhis_token, user = dhis_user, pwd = dhis_pwd,
                            dryRun = dryRun)
    if resp.ok:
        logger.info("Sucessfully imported climate variables: %s", variables)
        logger.debug("Response: %s", resp.text)
    else:
        logger.error("Failed Import: %s", variables)
        logger.error("Response: %s", resp.text)
        
    return
