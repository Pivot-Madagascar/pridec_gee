import json
import ee

from pridec_gee import fetch_sen1_flood

#initialize (should be done in conftest.py)
ee.Authenticate()
ee.Initialize(project='ee-mevans-pridec')

def test_sen1_flood_downloads():

    #replace with test polygon
    rice_geojson_file = "data/major-rice-orgUnit.geojson"
    with open(rice_geojson_file) as f:
        geojson_data = json.load(f)

    rice_fields = ee.FeatureCollection(geojson_data)

    date_range = {
        "start_label": "202501",
        "end_label": "202502",
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-02-28"
    }

    output = fetch_sen1_flood(rice_features=rice_fields, date_range=date_range, test_run=True)

    print(output)

test_sen1_flood_downloads()