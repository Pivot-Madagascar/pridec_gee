import os
from dotenv import load_dotenv
load_dotenv(override=True)

dhis_url = os.environ.get("DHIS2_URL")
dhis_token = os.getenv("DHIS2_TOKEN")

from pridec_gee import get_pridec_elements

def test_get_pridec_de():

    get_pridec_elements(dhis_url = dhis_url, dhis_token=dhis_token)