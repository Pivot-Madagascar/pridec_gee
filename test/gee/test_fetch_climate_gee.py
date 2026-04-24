import ee
import pytest

from pridec_gee import fetch_climate_gee, AVAILABLE_VARIABLES

debug=False
if debug:
    import json
    import os
    from dotenv import load_dotenv
    load_dotenv()
    ee.Authenticate()
    ee.Initialize(project=os.getenv("GEE_PROJECT"))
    #testing on local gee-test instance

    geojson_path = "test/data/test_polygons.geojson"
    with open(geojson_path, 'r') as f:
        test_polygons = json.load(f)

    geojson_path = "test/data/rice_subset.geojson"
    with open(geojson_path, 'r') as f:
            test_ricefields = json.load(f)
    import logging

    logger = logging.getLogger(__name__)

def test_fetch_pridec_gee(test_ricefields, test_polygons, gee_service_account, gee_key):

    credentials = ee.ServiceAccountCredentials(gee_service_account, gee_key)
    ee.Initialize(credentials)

    rice_fields = ee.FeatureCollection(test_ricefields)
    orgUnit = ee.FeatureCollection(test_polygons)

    date_range = {
        "start_date_gee":"2025-04-01",
        "end_date_gee": "2025-07-30"
    }

    output = fetch_climate_gee(orgUnit = orgUnit, date_range = date_range, rice_features = rice_fields)

    assert bool(output.query("period == '202504' and dataElement == 'pridec_climate_temperatureMean'")["value"].iloc[0] == 23.0288)
    assert set(output["dataElement"].unique()) == set(AVAILABLE_VARIABLES)