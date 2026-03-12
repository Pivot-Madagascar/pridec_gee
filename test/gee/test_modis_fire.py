import ee

from pridec_gee import fetch_modis_fire

debug=False
if debug:
    import json
    import os
    from dotenv import load_dotenv
    load_dotenv()
    ee.Authenticate()
    ee.Initialize(project=os.getenv("GEE_PROJECT"))
    geojson_path = "tests/data/test_polygons.geojson"
    with open(geojson_path, 'r') as f:
        test_polygons = json.load(f)

def test_modis_fire_downloads(test_polygons, gee_service_account, gee_key):

    #gee authentication
    credentials = ee.ServiceAccountCredentials(gee_service_account, gee_key)
    ee.Initialize(credentials)

    orgUnit = ee.FeatureCollection(test_polygons)

    date_range = {
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-01-30"
    }

    output = fetch_modis_fire(orgUnit, date_range)

    assert output['dataValues'][0]['value'] == 0.008814