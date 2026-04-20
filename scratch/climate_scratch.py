
#activate env and install packages first
#source .venv/bin/activate

import ee
import pandas as pd
from dateutil.relativedelta import relativedelta


from utils.get_dhis_geojson import get_dhis_geojson
from utils.gee_utils import month_agg_sp_mean
from utils.get_date_range import get_date_range
import os

## Set up Configurations
# GEE initialization
ee.Authenticate() #eventaully use token from environment
ee.Initialize(project='ee-mevans-pridec') # also determined via env variable

DHIS_TOKEN = os.environ.get("TOKEN_DHIS_PRIDEC_MICHELLE")
DHIS_URL = os.environ.get("DHIS_URL_PRIDEC")
PARENT_OU = os.environ.get("PARENT_OU_ID") #corresponds to ifanadiana
OU_LEVEL = 6 #fokontany

# Headers for token-based auth
headers = {
    "Authorization": f"ApiToken {DHIS_TOKEN}"
}

# -----------------------get geojson from DHIS2
org_units = get_dhis_geojson(PARENT_OU=PARENT_OU, OU_LEVEL=OU_LEVEL, DHIS_TOKEN=DHIS_TOKEN, DHIS_URL=DHIS_URL)

#save if you want
# with open("fkt_orgUnit_dhis.geojson", "w") as f:
#     json.dump(org_units, f, indent  = 2)

#turn into ee object
orgUnit = ee.FeatureCollection(org_units)

#-----------------------------set date range-----------------------------#
date_range =  get_date_range(start_months_ago = 3,
                             end_on_last_day=False)
#format for GEE and labels
start_label = start_date.strftime("%Y%m")
end_label = end_date.strftime("%Y%m")
start_date_gee = start_date.strftime("%Y-%m-%d")
end_date_gee = end_date.strftime("%Y-%m-%d")

#----------------------------FEWSNET: Humidity and Windspeed------------#
fewsnet_ic = ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001").filterBounds(orgUnit).filterDate("2010-01-01", today)

#fewsnet has a longer delay and so needs a different end_date of two months ago
end_date_fews = this_month_first - relativedelta(months=2)
end_date_fews_gee = end_date_fews.strftime("%Y-%m-%d")

#define parameters for functions
fews_fxparams = {
    'reducer': ee.Reducer.mean(),  # Change the reducer if needed
    'bands': ['Qair_f_tavg', 'Wind_f_tavg'],  # Example bands
    'bandsRename': ['humidity_fews', "windspeed_fews"]  # Rename bands
}

#return a table of data, will take several minutes
fews_result = month_agg_sp_mean(fewsnet_ic, orgUnit, start_date_gee, end_date_fews_gee, fews_fxparams)

# As a pandas object
df = pd.DataFrame(fews_result)
print(df.head())

#format for dhis and post as json
#rrename columns to match pridec output
df = df.rename(columns={
    'humidity_fews_mean': 'pridec_climate_relHumidity',
    'windspeed_fews_mean': 'pridec_climate_windSpeed'
})

#pivot to long format for eventual json
df_long = df.melt(
    id_vars=['orgUnit', 'period'],
    var_name='dataElement',
    value_name='value'
)

# Drop missing values
df_long = df_long.dropna(subset=['value'])

# Round values
df_long['value'] = df_long['value'].round(4)

# Ensure period is string
df_long['period'] = df_long['period'].astype(str)

print(df_long.head())

#turn into json and post