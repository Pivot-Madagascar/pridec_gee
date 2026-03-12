import ee

from pridec_gee import fetch_sen1_flood

debug=False
if debug:
    import json
    import os
    from dotenv import load_dotenv
    load_dotenv()
    ee.Authenticate()
    ee.Initialize(project=os.getenv("GEE_PROJECT"))
    geojson_path = "test/data/rice_subset.geojson"
    with open(geojson_path, 'r') as f:
        test_ricefields = json.load(f)

def test_sen1_flood_downloads(test_ricefields, gee_service_account, gee_key):

    credentials = ee.ServiceAccountCredentials(gee_service_account, gee_key)
    ee.Initialize(credentials)

    rice_fields = ee.FeatureCollection(test_ricefields)

    date_range = {
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-02-28"
    }

    output = fetch_sen1_flood(rice_features=rice_fields, date_range=date_range, test_run=True)

    assert output['dataValues'][14]['value'] == 0.182123   