import os
from pathlib import Path
import json
from dotenv import load_dotenv
import requests
import pytest

load_dotenv()



@pytest.fixture(scope="session")
def api_connection():
    url = f"{os.getenv("DHIS_URL").rstrip('/')}/api/system/info"
    token = os.getenv("DHIS_TOKEN")
    headers = {'Authorization': f'ApiToken {token}'} 

    try:
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
    except requests.RequestException as e:
        pytest.skip(f"API not reachable: {e}")

@pytest.fixture(scope="session")
def dhis_token():
    token = os.getenv("DHIS_TOKEN")
    if token is None:
        pytest.skip("No DHIS2 API token available")
    return token

@pytest.fixture(scope="session")
def dhis_url():
    url = os.getenv("DHIS_URL")
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
    if  not path.is_file():
        pytest.skip("No GEE Private Key Available")
    return ".gee-private-key.json"

@pytest.fixture
def test_polygons():
    geojson_path = "test/data/test_polygons.geojson"
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    return geojson_data

@pytest.fixture
def test_ricefields():
    geojson_path = "test/data/rice_subset.geojson"
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    return geojson_data