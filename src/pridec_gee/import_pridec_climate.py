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

def import_pridec_climate(dhis_url, date_range, orgUnit=None, parent_ou=None, ou_level=None, 
                       variables=["fewsnet","era5", "modis_aod", "modis_fire", "sen2", "sen1_flood"], 
                       rice_features=None,
                       dhis_user=None, dhis_pwd=None, dhis_token=None, dryRun=True,
                       verbose=True):
    """
    Import PRIDE-C variables into a DHIS2 instance

    Args:
        dhis_url (str)                      url of dhis2 instance
        orgUnit (FeatureCollection, opt)    FeatureCollection of orgUnits to download
        parent_ou (str, Optional)           uid of parent orgUnit for geojson download
        ou_level (int, Optional)            hierarchical level of orgUnit to extract for
        date_range (list)                   date_range (dict): range of dates to download data of. 
                                                Format is a string (start_label [%Y%m], end_label[%Y%m], start_date_gee[%Y-%m-%d], end_date_gee[%Y-%m-%d])  
        variables (list)                    list containing all or a subset of the following:
                                                ["fewsnet","era5", "modis_aod", "modis_fire", "sen2", "sen1_flood"]
        rice_features                       ee.Feature Collection of rice fields if importing `sen1_flood` data
        dhis_user (str, optional)           username for dhis2 instance
        dhis_pwd (str, optional)            password for dhis2 instance
        dhis_token (str, optional)          personal access token for dhis2 instance.
                                            Can be provided instead of user and pwd.
        dryRun (boolean)                    True: test a dry run of the POST
                                            False: actually post the data
        verbose (boolean)                   Return API responses from DHIS2 POST?

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
            if verbose:
                logger.info("Response: %s", resp.text)
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
            if verbose:
                logger.info("Response: %s", resp.text)
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
            if verbose:
                logger.info("Response: %s", resp.text)
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
            if verbose:
                logger.info("Response: %s", resp.text)
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
            if verbose:
                logger.info("Response: %s", resp.text)
        else:
            logger.error("Failed to import Sen2 Vegetation Indicators")
            logger.error("Response: %s", resp.text)
    
    if "sen1_flood" in variables:
        if rice_features is None:
            logger.error("Argument rice_features must be provided to import Sen-1 Ricefield flooding dynamics")
            return
        
        logger.info("Importing Sen-1 flood data. This can take 30-45 minutes if not in dryRun mode.")

        flood_json = fetch_sen1_flood(rice_features, date_range, dryRun)
        resp = post_climate(base_url = dhis_url, payload = flood_json, 
                            token = dhis_token, user = dhis_user, pwd = dhis_pwd,
                            dryRun = dryRun)
        if resp.ok:
            logger.info("Sen1 Flooding Dynamics imported")
            if verbose:
                logger.info("Response: %s", resp.text)
        else:
            logger.error("Failed to import Sen1 Flooding Dynamics")
            logger.error("Response: %s", resp.text)
        
    return
