#activate env and install packages first
#source venv/bin/activate

import ee
import pandas as pd
import geemap
import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

#in-house utility functions
from utils import *
from utils.gee_s1_ard import *

# set up configurations ################
ee.Authenticate() #eventaully use token from environment
ee.Initialize(project=os.environ.get("GEE_PROJECT"))

DHIS_TOKEN = os.environ.get("TOKEN_DHIS_PRIDEC_MICHELLE")
DHIS_URL = os.environ.get("DHIS_URL_PRIDEC")
TEST_DHIS_URL = "localhost:8080" #for testing post without touching the prod server
PARENT_OU = os.environ.get("PARENT_OU_ID") #corresponds to ifanadiana
OU_LEVEL = 6 #fokontany

#Get orgUnits once to save time #######################
# orgUnits can be accessd within each fetch call or here and then provided to the fetch call
# I wasn't srue what was easiest for the flask app. see both options below

org_units = get_dhis_geojson(PARENT_OU=PARENT_OU, OU_LEVEL=OU_LEVEL, dhis_tokken=DHIS_TOKEN, dhis_url=DHIS_URL)
orgUnit = ee.FeatureCollection(org_units)

# FEWSNET ############################################

fewsnet_json = fetch_fewsnet_windSpeed(DHIS_TOKEN=DHIS_TOKEN, 
                                       DHIS_URL = DHIS_URL,
                                       PARENT_OU = PARENT_OU,
                                       OU_LEVEL = OU_LEVEL)

#function to post to instance
post_dataValues

# MODIS Aerosol Optical Depth ########################

aod_json = fetch_modis_aod(DHIS_TOKEN = DHIS_TOKEN, 
                           DHIS_URL = DHIS_URL,
                           PARENT_OU = PARENT_OU,
                           OU_LEVEL = OU_LEVEL,
                           orgUnit = orgUnit)

#function to post to instance

# MODIS Proportion bush fire ########################

fire_json = fetch_modis_fire(DHIS_TOKEN = DHIS_TOKEN, 
                             DHIS_URL = DHIS_URL, 
                             PARENT_OU=PARENT_OU,
                             OU_LEVEL=OU_LEVEL,
                             orgUnit = orgUnit)

#function to post to instance

# ERA5: temperature, precipitation, relative humidity ############

era5_json = fetch_era5_climate(orgUnit=orgUnit)
#post to instance

# Sen 2: EVI, MDNWI, GAO ######################################

sen2_json = fetch_sen2_climate(orgUnit = orgUnit)

# Sen1 : Ricefield Flooding ###################################



