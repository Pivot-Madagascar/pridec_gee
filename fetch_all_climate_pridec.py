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
load_dotenv()

#in-house utility functions
from utils import *
from utils.gee_s1_ard import *

# set up configurations ################
ee.Authenticate() #eventaully use token from environment
ee.Initialize(project=os.environ.get("GEE_PROJECT"))

# DHIS_TOKEN = os.environ.get("TOKEN_DHIS_PRIDEC_MICHELLE")
# DHIS_URL = os.environ.get("DHIS_URL_PRIDEC")
TEST_URL = "http://localhost:8080/" #for testing 
TEST_TOKEN= "d2pat_XAbi5ElPPRiFZTpT3dxxa7ZYEAeFtxMX3440051476" #need to reinitilize on your own local server
PARENT_OU = "VtP4BdCeXIo" #corresponds to ifanadiana
OU_LEVEL = 6 #fokontany

#Get orgUnits once to save time #######################
# orgUnits can be accessd within each fetch call or here and then provided to the fetch call
# I wasn't srue what was easiest for the flask app. see both options below

org_units = get_dhis_geojson(PARENT_OU=PARENT_OU, OU_LEVEL=OU_LEVEL, dhis_token=TEST_TOKEN, dhis_url=TEST_URL)
orgUnit = ee.FeatureCollection(org_units)

# FEWSNET ############################################

#example fetching orgUnits within the fetch call
fewsnet_json = fetch_fewsnet_windSpeed(dhis_token = TEST_TOKEN, 
                                       dhis_url = TEST_URL,
                                       PARENT_OU = PARENT_OU,
                                       OU_LEVEL = OU_LEVEL)

#function to post to instance
resp = post_dataValues(base_url = TEST_URL, payload = fewsnet_json, token = TEST_TOKEN, dryRun = True)
print(resp)

# MODIS Aerosol Optical Depth ########################

#example using already available orgUnit
aod_json = fetch_modis_aod(orgUnit = orgUnit)

resp = post_dataValues(base_url = TEST_URL, payload = aod_json, token = TEST_TOKEN, dryRun = True)
print(resp)

# MODIS Proportion bush fire ########################

fire_json = fetch_modis_fire(orgUnit = orgUnit)

resp = post_dataValues(base_url = TEST_URL, payload = fire_json, token = TEST_TOKEN, dryRun = True)
print(resp)

# ERA5: temperature, precipitation, relative humidity ############

era5_json = fetch_era5_climate(orgUnit=orgUnit)

#test one payload
payload_test = {
    "dataValues": [
        {
        "orgUnit": "NKnlmpvCHID",
        "period": "202510",
        "dataElement": "pridec_climate_temperatureMean",
        "value": 17.7288
    }
    ]
}

#post to instance
resp = post_dataValues(base_url = TEST_URL, payload = era5_json, token = TEST_TOKEN, dryRun = True)
print(resp)

# Sen 2: EVI, MDNWI, GAO ######################################

sen2_json = fetch_sen2_climate(orgUnit = orgUnit)

resp = post_dataValues(base_url = TEST_URL, payload = sen2_json, token = TEST_TOKEN, dryRun = True)
print(resp)

# Sen1 : Ricefield Flooding ###################################

#still debugging GEE code for python

