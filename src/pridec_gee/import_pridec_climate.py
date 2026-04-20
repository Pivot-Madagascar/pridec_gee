import ee
import datetime
import logging

logger = logging.getLogger(__name__)

from .gee.fetch_fewsnet_windspeed import fetch_fewsnet_windspeed
from .gee.fetch_era5_climate import fetch_era5_climate
from .gee.fetch_modis_aod import fetch_modis_aod
from .gee.fetch_modis_fire import fetch_modis_fire
from .gee.fetch_sen1_flood import fetch_sen1_flood
from .gee.fetch_sen2_indicators import fetch_sen2_indicators
from .dhis2.get_dhis_geojson import get_dhis_geojson
from .dhis2.post_climate import post_climate

def import_pridec_climate(
    dhis_url: str,
    date_range: dict[str, str],
    orgUnit: ee.FeatureCollection = None,
    parent_ou: str = None,
    ou_level: int = None,
    variables: list[str] = ["fewsnet","era5", "modis_aod", "modis_fire", "sen2", "sen1_flood"],
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
        variables: List of variables to import. Defaults to all:
            ["fewsnet","era5", "modis_aod", "modis_fire", "sen2", "sen1_flood"].
        rice_features: FeatureCollection of rice fields if importing `sen1_flood` data.
        dhis_user: Username for DHIS2 instance (optional).
        dhis_pwd: Password for DHIS2 instance (optional).
        dhis_token: Personal access token for DHIS2. Can be used instead of `dhis_user`/`dhis_pwd`.
        dryRun: If True, performs a dry run without posting data and using only 5 `sen1_flood` images. Defaults to True.

    Returns:
        requests.Response: Response object from POST requests
    """

    logger.info("Updating PRIDEC Climate variables for %s",
                dhis_url)
    logger.info("Using configuration dryRun = %s", dryRun)



    if orgUnit is None:
        logger.info("Fetching geojson for parent %s at level %s",
                    parent_ou, ou_level)
        org_units = get_dhis_geojson(parent_ou=parent_ou, ou_level=ou_level, 
                                    dhis_token=dhis_token, dhis_user=dhis_user, dhis_pwd=dhis_pwd, dhis_url=dhis_url)
        orgUnit = ee.FeatureCollection(org_units)

    if 'fewsnet' in variables:
        logger.info("Importing FEWSNET windspeed")
        fewsnet_json = fetch_fewsnet_windspeed(orgUnit, date_range)
        resp = post_climate(base_url = dhis_url, payload = fewsnet_json, 
                            token = dhis_token, user = dhis_user, pwd = dhis_pwd,
                            dryRun = dryRun)
        if resp.ok:
            logger.info("Imported FEWSNET windspeed")
            logger.debug("Response: %s", resp.text)
        else:
            logger.error("Failed to import FEWSNET windspeed")
            logger.error("Response: %s", resp.text)
    
    if "era5" in variables:
        logger.info("Importing ERA5 climate variables")
        era5_json = fetch_era5_climate(orgUnit, date_range)
        resp = post_climate(base_url = dhis_url, payload = era5_json, 
                            token = dhis_token, user = dhis_user, pwd = dhis_pwd,
                            dryRun = dryRun)
        if resp.ok:
            logger.info("Imported ERA5 climate variables")
            logger.debug("Response: %s", resp.text)
        else:
            logger.error("Failed to import ERA5 climate variables")
            logger.error("Response: %s", resp.text)

    if "modis_aod" in variables:
        logger.info("Importing MODIS Aerosol Optical Depth")
        aod_json = fetch_modis_aod(orgUnit, date_range)
        resp = post_climate(base_url = dhis_url, payload = aod_json, 
                            token = dhis_token, user = dhis_user, pwd = dhis_pwd,
                            dryRun = dryRun)
        if resp.ok:
            logger.info("Imported MODIS Aerosol Optical Depth")
            logger.debug("Response: %s", resp.text)
        else:
            logger.error("Failed to import MODIS Aerosol Optical Depth")
            logger.error("Response: %s", resp.text)
    
    if "modis_fire" in variables:
        logger.info("Importing MODIS Fire Detection")

        fire_json = fetch_modis_fire(orgUnit, date_range)
        resp = post_climate(base_url = dhis_url, payload = fire_json, 
                            token = dhis_token, user = dhis_user, pwd = dhis_pwd,
                            dryRun = dryRun)
        if resp.ok:
            logger.info("Imported MODIS Fire Detection")
            logger.debug("Response: %s", resp.text)
        else:
            logger.error("Failed to import MODIS Fire Detection")
            logger.error("Response: %s", resp.text)

    

    if "sen2" in variables:
        logger.info("Importing Sen2 Vegetation Indicators")
        sen2_json = fetch_sen2_indicators(orgUnit, date_range)
        resp = post_climate(base_url = dhis_url, payload = sen2_json, 
                            token = dhis_token, user = dhis_user, pwd = dhis_pwd,
                            dryRun = dryRun)
        if resp.ok:
            logger.info("Imported Sen2 Vegetation Indicators")
            logger.debug("Response: %s", resp.text)
        else:
            logger.error("Failed to import Sen2 Vegetation Indicators")
            logger.error("Response: %s", resp.text)
    
    if "sen1_flood" in variables:
        if rice_features is None:
            logger.error("Argument rice_features must be provided to import Sen-1 Ricefield flooding dynamics")
            return
        
        logger.info("Importing Sen-1 flood data. This can take 30-45 minutes if not in dryRun mode. Currently running with dryRun = %s", dryRun)

        flood_json = fetch_sen1_flood(rice_features, date_range, dryRun)
        resp = post_climate(base_url = dhis_url, payload = flood_json, 
                            token = dhis_token, user = dhis_user, pwd = dhis_pwd,
                            dryRun = dryRun)
        if resp.ok:
            logger.info("Sen1 Flooding Dynamics imported")
            logger.debug("Response: %s", resp.text)
        else:
            logger.error("Failed to import Sen1 Flooding Dynamics")
            logger.error("Response: %s", resp.text)
        
    return
