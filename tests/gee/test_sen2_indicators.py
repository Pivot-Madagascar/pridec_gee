import json
import ee

# from pridec_gee import fetch_sen2_indicators

from src.pridec_gee.gee.fetch_sen2_indicators import fetch_sen2_indicators

#initialize (should be done in conftest.py)
ee.Authenticate()
ee.Initialize(project='ee-mevans-pridec')

def test_sen2_inds_downloads():

    #replace with test polygon
    geojson_path = "scratch/csb_orgUnit_dhis.geojson"
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)

    orgUnit = ee.FeatureCollection(geojson_data)

    date_range = {
        "start_date_gee":"2024-01-01",
        "end_date_gee": "2024-02-28"
    }

    climate_data = fetch_sen2_indicators(orgUnit, date_range)

    print(climate_data)

test_sen2_inds_downloads()