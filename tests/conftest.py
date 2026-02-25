import os
import pytest

@pytest.fixture(scope="session")
def api_token():
    token = os.getenv("DHIS2_TOKEN")
    if token is None:
        pytest.skip("No API token available")
    return token