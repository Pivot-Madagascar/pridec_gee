from pridec_gee import delete_historic_climate
import pytest

debug=False
if debug:
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    dhis_url = os.environ.get("DHIS_URL")
    dhis_token = os.getenv("DHIS_TOKEN")

def test_delete_historic_climate_connects(dhis_url, dhis_token, api_connection):
    
    resp = delete_historic_climate(base_url=dhis_url,
                            token=dhis_token,
                            orgUnit_ids=["O1wNJut8eci"],
                            dataElement='pridec_climate_evi',
                            delete_month_range=['202001', '202002'],
                            dryRun = True)
    
    assert resp.ok

#should write a function to ensure it actually deletes too

def test_delete_historic_error_noUser(dhis_url):
    with pytest.raises(ValueError):
        delete_historic_climate(base_url=dhis_url,
                            user=None,
                            pwd="secret",
                            orgUnit_ids=["O1wNJut8eci"],
                            dataElement='pridec_climate_evi',
                            delete_month_range=['202001', '202002'],
                            dryRun = True)
        
def test_delete_historic_error_noPwd(dhis_url):
    with pytest.raises(ValueError):
        delete_historic_climate(base_url=dhis_url,
                            user="user",
                            pwd=None,
                            orgUnit_ids=["O1wNJut8eci"],
                            dataElement='pridec_climate_evi',
                            delete_month_range=['202001', '202002'],
                            dryRun = True)


