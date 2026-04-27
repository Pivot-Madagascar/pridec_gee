import ee
import pytest

from pridec_gee import import_pridec_climate, AVAILABLE_VARIABLES

debug=False
if debug:
    import json
    import os
    from dotenv import load_dotenv
    load_dotenv()
    ee.Authenticate()
    ee.Initialize(project=os.getenv("GEE_PROJECT"))
    #testing on local gee-test instance
    dhis_token = os.getenv("DHIS_TOKEN")
    dhis_url = os.getenv("DHIS_URL")
    parent_ou = os.getenv("PARENT_OU")
    OU_LEVEL = 5 #fokontany
    dryRun = True #default dryRun = True

    geojson_path = "test/data/test_polygons.geojson"
    with open(geojson_path, 'r') as f:
        test_polygons = json.load(f)

    geojson_path = "test/data/rice_subset.geojson"
    with open(geojson_path, 'r') as f:
            test_ricefields = json.load(f)
    import logging

    logger = logging.getLogger(__name__)


def test_import_pridec_climate(test_ricefields, test_polygons, gee_service_account, gee_key,
                               dhis_url, dhis_token, api_connection):

    credentials = ee.ServiceAccountCredentials(gee_service_account, gee_key)
    ee.Initialize(credentials)

    rice_fields = ee.FeatureCollection(test_ricefields)
    orgUnit = ee.FeatureCollection(test_polygons)

    date_range = {
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-02-28"
    }

    import_pridec_climate(dhis_url=dhis_url, date_range=date_range, orgUnit=orgUnit,
                          rice_features=rice_fields, dhis_token=dhis_token, dryRun=True)
    
    with pytest.raises(ValueError, match="Invalid variable"):
        import_pridec_climate(dhis_url=dhis_url, date_range=date_range, orgUnit=orgUnit, variables = ["pridec_climate_wrong"],
                          rice_features=rice_fields, dhis_token=dhis_token, dryRun=True)
    



