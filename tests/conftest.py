import os
from pathlib import Path
import json
import ee

import pytest

@pytest.fixture(scope="session")
def dhis_token():
    token = os.getenv("DHIS2_TOKEN")
    if token is None:
        pytest.skip("No DHIS2 API token available")
    return token

@pytest.fixture(scope="session")
def dhis_url():
    url = os.getenv("DHIS2_URL")
    if url is None:
        pytest.skip("No DHIS2 URL available")
    return url

@pytest.fixture(scope="session")
def gee_project():
    proj = os.getenv("GEE_PROJECT")
    if proj is None:
        pytest.skip("No GEE Project available")
    return proj

@pytest.fixture(scope="session")
def gee_service_account():
    account = os.getenv("GEE_SERVICE_ACCOUNT")
    if account is None:
        pytest.skip("No GEE Service Account available")
    return account

@pytest.fixture(scope="session")
def gee_key():
    path = Path(".gee-private-key.json")
    if path is None:
        pytest.skip("No GEE Private Key Available")
    return path

@pytest.fixture
def test_polygons():
    geojson_path = Path(__file__).parents[1] / "data/test_polygons.geojson"
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    return geojson_data

@pytest.fixture
def test_ricefields():
    geojson_path = Path(__file__).parents[1] / "data/rice_subset.geojson"
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    return geojson_data