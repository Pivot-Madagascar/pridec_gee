import ee
import os
from pridec_gee import fetch_era5_climate, get_dhis_geojson, fetch_climate_gee, AVAILABLE_VARIABLES
from dotenv import load_dotenv

load_dotenv()

GEE_PROJECT=os.getenv("GEE_PROJECT") # replace with your GEE project name
#initialize GEE account
ee.Authenticate()
ee.Initialize(project=GEE_PROJECT)

#get polygons from DHIS2 instance
DHIS_URL="https://play.im.dhis2.org/stable-2-40-11/"
DHIS_USER='admin'
DHIS_PWD='district'

test_polygons = get_dhis_geojson(parent_ou= "Vth0fbpFcsO",
                     ou_level="3",
                     dhis_url = DHIS_URL,
                     dhis_user = DHIS_USER,
                     dhis_pwd = DHIS_PWD)

orgUnit = ee.FeatureCollection(test_polygons)


date_range = {
    "start_date_gee":"2025-01-01",
    "end_date_gee": "2025-04-30"
}

#fetch a single variable
output = fetch_era5_climate(orgUnit, date_range)

print(output)

#fetch multiple variables
print(AVAILABLE_VARIABLES)
out_multiple = fetch_climate_gee(date_range = date_range, 
                                 orgUnit=orgUnit,
                                 variables = ['pridec_climate_mndwi', "pridec_climate_temperatureMean"])

out_multiple.head()

#to format for POSTing to DHIS2 instance, change to JSON dict called 'dataValues'
out_json = {
                    "dataValues": out_multiple.to_dict(orient="records")
                }
print(out_json)
