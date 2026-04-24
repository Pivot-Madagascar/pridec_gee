import ee
import pytest

from pridec_gee import fetch_era5_climate

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

def test_era5_climate_downloads(test_polygons, gee_service_account, gee_key):

    #initialize 
    credentials = ee.ServiceAccountCredentials(gee_service_account, gee_key)
    ee.Initialize(credentials)

    orgUnit = ee.FeatureCollection(test_polygons)

    date_range = {
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-01-30"
    }

    output = fetch_era5_climate(orgUnit, date_range, variables = ["pridec_climate_temperatureMean"])

    assert output['value'][2] == 23.8703
    assert all(output['dataElement']=="pridec_climate_temperatureMean")

def test_era5_climate_variableSelection(test_polygons, gee_service_account, gee_key):
        #initialize 
    credentials = ee.ServiceAccountCredentials(gee_service_account, gee_key)
    ee.Initialize(credentials)

    orgUnit = ee.FeatureCollection(test_polygons)

    date_range = {
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-01-30"
    }
    with pytest.raises(ValueError, match="Invalid variable"):
        fetch_era5_climate(orgUnit, date_range, variables = ["wrong_variable"])
