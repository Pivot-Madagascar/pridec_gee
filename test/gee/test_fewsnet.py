import ee

from pridec_gee import fetch_fewsnet_windspeed

debug=False
if debug:
    import json
    import os
    from dotenv import load_dotenv
    load_dotenv()
    ee.Authenticate()
    ee.Initialize(project=os.getenv("GEE_PROJECT"))
    geojson_path = "test/data/test_polygons.geojson"
    with open(geojson_path, 'r') as f:
        test_polygons = json.load(f)

def test_fewsnet_downloads(test_polygons, gee_service_account, gee_key):

    #initialize 
    credentials = ee.ServiceAccountCredentials(gee_service_account, gee_key)
    ee.Initialize(credentials)

    orgUnit = ee.FeatureCollection(test_polygons)

    date_range = {
        "start_date_gee":"2024-06-01",
        "end_date_gee": "2024-06-30"
    }

    output = fetch_fewsnet_windspeed(orgUnit, date_range)
    assert output['dataValues'][1]['value'] == 3.2199
