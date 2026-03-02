import json
import ee

import logging
logging.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s', level=logging.DEBUG)


from pridec_gee import import_pridec_climate

ee.Authenticate()
ee.Initialize(project='ee-mevans-pridec')
#testing on local geeTest instance
# dhis_token = "d2pat_aRxzyH9ifC50A5ye0EMxJjetxJxmSi9V0981737059"
dhis_token = "wrong_token"
dhis_url = "http://localhost:8080/"
# dhis_user="admin"
# dhis_pwd="Pridec_2025!"
dhis_user=None
dhis_pwd=None
parent_ou = "VtP4BdCeXIo" #corresponds to ifanadiana
OU_LEVEL = 6 #fokontany
dryRun = True #default dryRun = True

geojson_path = "tests/data/test_polygons.geojson"
with open(geojson_path, 'r') as f:
    test_polygons = json.load(f)
geojson_path = "tests/data/rice_subset.geojson"
with open(geojson_path, 'r') as f:
    test_ricefields = json.load(f)

rice_fields = ee.FeatureCollection(test_ricefields)
orgUnit = ee.FeatureCollection(test_polygons)

date_range = {
    "start_label": "202401",
    "end_label": "202402",
    "start_date_gee":"2024-01-01",
    "end_date_gee": "2024-02-28"
}

import_pridec_climate(dhis_url=dhis_url, date_range=date_range, orgUnit=orgUnit,
                    rice_features=rice_fields, dhis_token=dhis_token, dryRun=True,
                    variables=["era5"])

json_payload={'dataValues': [{'orgUnit': 'O1wNJut8eci', 'period': '202401', 'dataElement': 'pridec_climate_precipitation', 'value': 9.5453}, {'orgUnit': 'RRe6ic0AU1Z', 'period': '202401', 'dataElement': 'pridec_climate_precipitation', 'value': 9.6448}, {'orgUnit': 'r4U7PhBKR7S', 'period': '202401', 'dataElement': 'pridec_climate_precipitation', 'value': 9.3929}, {'orgUnit': 'O1wNJut8eci', 'period': '202402', 'dataElement': 'pridec_climate_precipitation', 'value': 24.2468}, {'orgUnit': 'RRe6ic0AU1Z', 'period': '202402', 'dataElement': 'pridec_climate_precipitation', 'value': 24.4395}, {'orgUnit': 'r4U7PhBKR7S', 'period': '202402', 'dataElement': 'pridec_climate_precipitation', 'value': 23.5805}, {'orgUnit': 'O1wNJut8eci', 'period': '202401', 'dataElement': 'pridec_climate_relHumidity', 'value': 86.3593}, {'orgUnit': 'RRe6ic0AU1Z', 'period': '202401', 'dataElement': 'pridec_climate_relHumidity', 'value': 87.1024}, {'orgUnit': 'r4U7PhBKR7S', 'period': '202401', 'dataElement': 'pridec_climate_relHumidity', 'value': 87.2287}, {'orgUnit': 'O1wNJut8eci', 'period': '202402', 'dataElement': 'pridec_climate_relHumidity', 'value': 92.0142}, {'orgUnit': 'RRe6ic0AU1Z', 'period': '202402', 'dataElement': 'pridec_climate_relHumidity', 'value': 92.5834}, {'orgUnit': 'r4U7PhBKR7S', 'period': '202402', 'dataElement': 'pridec_climate_relHumidity', 'value': 92.4811}, {'orgUnit': 'O1wNJut8eci', 'period': '202401', 'dataElement': 'pridec_climate_temperatureMean', 'value': 23.448}, {'orgUnit': 'RRe6ic0AU1Z', 'period': '202401', 'dataElement': 'pridec_climate_temperatureMean', 'value': 22.9106}, {'orgUnit': 'r4U7PhBKR7S', 'period': '202401', 'dataElement': 'pridec_climate_temperatureMean', 'value': 22.0843}, {'orgUnit': 'O1wNJut8eci', 'period': '202402', 'dataElement': 'pridec_climate_temperatureMean', 'value': 22.5375}, {'orgUnit': 'RRe6ic0AU1Z', 'period': '202402', 'dataElement': 'pridec_climate_temperatureMean', 'value': 21.9802}, {'orgUnit': 'r4U7PhBKR7S', 'period': '202402', 'dataElement': 'pridec_climate_temperatureMean', 'value': 21.164}]}