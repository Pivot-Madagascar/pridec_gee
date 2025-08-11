#activate env and install packages first
#source .venv/bin/activate

import ee
# import pandas as pd
# import json
# import requests
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
import os
from dotenv import load_dotenv
load_dotenv(override=True)

#in-house utility functions
from utils import *
from utils.gee_s1_ard import *

# set up configurations ################
credentials = ee.ServiceAccountCredentials(os.environ.get("GEE_SERVICE_ACCOUNT"), ".gee-private-key.json")
ee.Initialize(credentials)

#for interactive authentication
# ee.Authenticate() #eventaully use token from environment
# ee.Initialize(credentials, project=os.environ.get("GEE_PROJECT"))

DHIS_TOKEN = os.environ.get("DHIS2_TOKEN")
DHIS_URL = os.environ.get("DHIS2_PRIDEC_URL")
PARENT_OU = os.environ.get("PARENT_OU") #corresponds to ifanadiana
OU_LEVEL = 6 #fokontany
dryRun = os.getenv("DRYRUN", "true").lower() == "true" #default dryRun = True

print(f"🌐 Updating PRIDEC Climate variables for {DHIS_URL}")
print(f"🚧 Using configuration dryRun = {dryRun}")

#Get orgUnits once to save time #######################
# orgUnits can be accessd within each fetch call or here and then provided to the fetch call
# I wasn't srue what was easiest for the flask app. see both options below

print(f"📡 Fetching geojson for parent {PARENT_OU} at level {OU_LEVEL}")

org_units = get_dhis_geojson(PARENT_OU=PARENT_OU, OU_LEVEL=OU_LEVEL, dhis_token=DHIS_TOKEN, dhis_url=DHIS_URL)
orgUnit = ee.FeatureCollection(org_units)

# orgUnit_ids = orgUnit.aggregate_array('orgUnit').distinct().getInfo()

# FEWSNET ############################################

# print(f"Importing FEWSNET windspeed to {DHIS_URL}")

#example fetching orgUnits within the fetch call
fewsnet_json = fetch_fewsnet_windSpeed(dhis_token = DHIS_TOKEN, 
                                       dhis_url = DHIS_URL,
                                       PARENT_OU = PARENT_OU,
                                       OU_LEVEL = OU_LEVEL)

#function to post to instance
resp = post_dataValues(base_url = DHIS_URL, payload = fewsnet_json, token = DHIS_TOKEN, dryRun = dryRun)
# print(resp)

if resp.ok:
    print(f"✅ SUCCESS: Imported FEWSNET windspeed")
else:
    print(f"❌ Failed to import FEWSNET windspeed")
    print("Response:", resp.text)

# MODIS Aerosol Optical Depth ########################

# print(f"Importing MODIS AOD to {DHIS_URL}")

#example using already available orgUnit
aod_json = fetch_modis_aod(orgUnit = orgUnit)

resp = post_dataValues(base_url = DHIS_URL, payload = aod_json, token = DHIS_TOKEN, dryRun = dryRun)
# print(resp)

if resp.ok:
    print(f"✅ SUCCESS: Imported MODIS AOD")
else:
    print(f"❌ Failed to import MODIS AOD")
    print("Response:", resp.text)

# MODIS Proportion bush fire ########################

# print(f"Importing MODIS Fire to {DHIS_URL}")

fire_json = fetch_modis_fire(orgUnit = orgUnit)

resp = post_dataValues(base_url = DHIS_URL, payload = fire_json, token = DHIS_TOKEN, dryRun = dryRun)
# print(resp)

if resp.ok:
    print(f"✅ SUCCESS: Imported MODIS Fire")
else:
    print(f"❌ Failed to import MODIS Fire")
    print("Response:", resp.text)

# ERA5: temperature, precipitation, relative humidity ############

# print(f"Importing ERA5 Climate to {DHIS_URL}")

era5_json = fetch_era5_climate(orgUnit=orgUnit)

#post to instance
resp = post_dataValues(base_url = DHIS_URL, payload = era5_json, token = DHIS_TOKEN, dryRun = dryRun)
# print(resp)

if resp.ok:
    print(f"✅ SUCCESS: Imported ERA5 Climate")
else:
    print(f"❌ Failed to import ERA5 Climate")
    print("Response:", resp.text)

# Sen 2: EVI, MDNWI, GAO ######################################


#sen2_s2 begins 201804
sen2_json = fetch_sen2_climate(orgUnit = orgUnit)

resp = post_dataValues(base_url = DHIS_URL, payload = sen2_json, token = DHIS_TOKEN, dryRun = dryRun)
# print(resp)

if resp.ok:
    print(f"✅ SUCCESS: Imported Sentinel-2 Indicators")
else:
    print(f"❌ Failed to import Sentinel-2 Indicators")
    print("Response:", resp.text)

# Sen1 : Ricefield Flooding ###################################

print(f"🔎 Fetching Sen-1 flood data. This can take 30-45 minutes.")

flood_json = fetch_sen1_flood(rice_geojson_file="data/major-rice-orgUnit.geojson", 
                              test_run=dryRun)

resp = post_dataValues(base_url = DHIS_URL, payload = flood_json, token = DHIS_TOKEN, dryRun = dryRun)
# print(resp.json().get("response"))

if resp.ok:
    print(f"✅ SUCCESS: Imported Sen-1 Ricefield Flooding")
else:
    print(f"❌ Failed to import Sen-1 Ricefield Flooding")
    print("Response:", resp.text)

# Run analytics to update dataValues ################################

resp = launch_analytics(base_url = DHIS_URL, token = DHIS_TOKEN)

print(resp.json().get("response")['relativeNotifierEndpoint'])
analytics_endpoint = resp.json().get("response")['relativeNotifierEndpoint']

print(f"Launched rebuilding of Analytics Tables. View status at {DHIS_URL}{analytics_endpoint}")