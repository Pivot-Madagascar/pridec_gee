import json
import ee

import logging
logging.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s', level=logging.DEBUG)

from importlib.resources import files

import os
from dotenv import load_dotenv
load_dotenv(override=True)

from pridec_gee import import_pridec_climate
from pridec_gee import calc_date_range

# configs and env vars
credentials = ee.ServiceAccountCredentials(os.environ.get("GEE_SERVICE_ACCOUNT"), ".gee-private-key.json")
ee.Initialize(credentials)

dhis_token = os.environ.get("DHIS2_TOKEN")
dhis_url = os.environ.get("DHIS2_URL")
parent_ou = os.environ.get("PARENT_OU") #corresponds to ifanadiana
ou_level = 6 #fokontany
dryRun = os.getenv("DRYRUN", "true").lower() == "true" #default dryRun = True

#load rice fields 
geojson_path = files("pridec_gee").joinpath("data/pivot_major_rice.geojson")

with open(geojson_path, 'r') as f:
    rice_json = json.load(f)
rice_fields = ee.FeatureCollection(rice_json)

date_range = calc_date_range(start_months_ago=3,
                             end_on_last_day=True)

#will output to console 
import_pridec_climate(dhis_url=dhis_url,  dhis_token=dhis_token, date_range=date_range, 
                      orgUnit=None, parent_ou=parent_ou, ou_level=ou_level, #download from instance
                      variables= ["fewsnet", "era5", "modis_aod", "modis_fire", "sen2", "sen1_flood"],
                      rice_features=rice_fields, dryRun=dryRun)
