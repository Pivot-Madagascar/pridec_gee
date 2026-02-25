import json
import ee

# from pridec_gee import fetch_modis_fire

from src.pridec_gee.gee.fetch_modis_fire import fetch_modis_fire

#initialize (should be done in conftest.py)
ee.Authenticate()
ee.Initialize(project='ee-mevans-pridec')

def test_modis_fire_downloads():

    #replace with test polygon
    geojson_path = "scratch/csb_orgUnit_dhis.geojson"
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)

    orgUnit = ee.FeatureCollection(geojson_data)

    date_range = {
        "start_label": "202501",
        "end_label": "202504",
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-04-30"
    }

    climate_data = fetch_modis_fire(orgUnit, date_range)

    print(climate_data)

test_modis_fire_downloads()