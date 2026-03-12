from pridec_gee import get_pridec_elements

debug=False
if debug:
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    dhis_url = os.environ.get("DHIS_URL")
    dhis_token = os.getenv("DHIS_TOKEN")

def test_get_pridec_elements(dhis_url, dhis_token, api_connection):

    output = get_pridec_elements(dhis_url=dhis_url, dhis_token=dhis_token)

    assert output[0]['code'] == 'pridec_climate_AOD'
    assert len(output)==11
