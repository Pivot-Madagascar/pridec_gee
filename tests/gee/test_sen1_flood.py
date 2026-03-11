import ee

from pridec_gee import fetch_sen1_flood

#initialize (should be done in conftest.py)
# ee.Authenticate()
# ee.Initialize(project='ee-mevans-pridec')

def test_sen1_flood_downloads(test_ricefields, gee_service_account, gee_key):

    credentials = ee.ServiceAccountCredentials(gee_service_account, gee_key)
    ee.Initialize(credentials)

    #replace with test polygon
    # rice_geojson_file = "tests/data/rice_subset.geojson"
    # with open(rice_geojson_file) as f:
    #     test_ricefields = json.load(f)

    rice_fields = ee.FeatureCollection(test_ricefields)

    date_range = {
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-02-28"
    }

    output = fetch_sen1_flood(rice_features=rice_fields, date_range=date_range, test_run=True)

    print(output)

# test_sen1_flood_downloads()