#activate env and install packages first
#source .venv/bin/activate

import ee
import pandas as pd
import geemap
import json
from utils import zonal_stats, month_agg_sp_mean

ee.Authenticate()

ee.Initialize(project='ee-mevans-pridec')
# testing with FEWSNET
# orgUnit = ee.FeatureCollection("projects/ee-pridec/assets/spatial-admin/fkt_polygon")
#or read in a geojson file
geojson_path = "ifd_fokontany2.geojson"
with open(geojson_path, 'r') as f:
    geojson_data = json.load(f)

orgUnit = ee.FeatureCollection(geojson_data)

#set date period
startDate = '2015-01-01'
endDate = '2015-03-01'

#fewsnet image collection, spatially filtered to save time
ic = ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001").filterBounds(orgUnit)

#define parameters for functions
fxparams = {
    'reducer': ee.Reducer.mean(),  # Change the reducer if needed
    'bands': ['Qair_f_tavg', 'Wind_f_tavg'],  # Example bands
    'bandsRename': ['humidity_fews', "windspeed_fews"]  # Rename bands
}

#reurnign just images
result = zonal_stats(ic, orgUnit, fxparams)

print(result)

#testing the full spatial aggregation and returning a table
test_result = month_agg_sp_mean(ic, orgUnit, startDate, endDate, fxparams)

print(test_result)
print(type(test_result))

# As a pandas object
df = pd.DataFrame(test_result)

# Print the first few rows to check
print("\nResults as DataFrame:")
print(df.head())

#As a json
# would need to add some format so this could immediately be sent to DHIS2
df.to_json(orient = "index")

