
import json
import ee

from pridec_gee import fetch_era5_climate


def test_era5_climate_downloads(test_polygons, gee_service_account, gee_key):

    #initialize (should be done in conftest.py)
    credentials = ee.ServiceAccountCredentials(gee_service_account, gee_key)
    ee.Initialize(credentials)


    # #replace with test polygon
    # geojson_path = "tests/data/test_polygons.geojson"
    # with open(geojson_path, 'r') as f:
    #     test_polygons = json.load(f)

    orgUnit = ee.FeatureCollection(test_polygons)

    date_range = {
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-01-30"
    }

    output = fetch_era5_climate(orgUnit, date_range)

    assert output['dataValues'][6]['value'] == 25.3665
