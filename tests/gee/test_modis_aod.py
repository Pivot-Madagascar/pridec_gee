import json
import ee

from pridec_gee import fetch_modis_aod

#initialize (should be done in conftest.py)
ee.Authenticate()
ee.Initialize(project='ee-mevans-pridec')

def test_modis_aod_downloads():

    #replace with test polygon
    geojson_path = "scratch/csb_orgUnit_dhis.geojson"
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)

    orgUnit = ee.FeatureCollection(geojson_data)

    date_range = {
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-04-30"
    }

    climate_data = fetch_modis_aod(orgUnit, date_range)

    print(climate_data)

test_modis_aod_downloads()