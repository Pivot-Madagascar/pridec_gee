import json
import ee
from pathlib import Path


from pridec_gee import import_pridec_climate

# from src.pridec_gee import import_pridec_climate

#initialize (should be done in conftest.py)
debug=False
if debug:
    ee.Authenticate()
    ee.Initialize(project='ee-mevans-pridec')
    #testing on local gee-test instance
    dhis_token = "d2pat_XAbi5ElPPRiFZTpT3dxxa7ZYEAeFtxMX3440051476"
    dhis_url = "http://localhost:8080/"
    parent_ouU = "VtP4BdCeXIo" #corresponds to ifanadiana
    OU_LEVEL = 6 #fokontany
    dryRun = True #default dryRun = True

    geojson_path = "tests/data/test_polygons.geojson"
    with open(geojson_path, 'r') as f:
        test_polygons = json.load(f)

    geojson_path = "tests/data/rice_subset.geojson"
    with open(geojson_path, 'r') as f:
            test_ricefields = json.load(f)


def test_import_pridec_climate(test_ricefields, test_polygons, gee_service_account, gee_key,
                               dhis_url, dhis_token):

    credentials = ee.ServiceAccountCredentials(gee_service_account, gee_key)
    ee.Initialize(credentials)

    rice_fields = ee.FeatureCollection(test_ricefields)
    orgUnit = ee.FeatureCollection(test_polygons)

    date_range = {
        "start_label": "202501",
        "end_label": "202502",
        "start_date_gee":"2025-01-01",
        "end_date_gee": "2025-02-28"
    }

    import_pridec_climate(dhis_url=dhis_url, date_range=date_range, orgUnit=orgUnit,
                          rice_features=rice_fields, dhis_token=dhis_token, dryRun=True)



