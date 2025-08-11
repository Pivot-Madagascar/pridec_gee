#code to delete lots of historic data and then update

resp = delete_historic_climate(base_url = DHIS_URL, dataElement = "pridec_climate_evi", delete_months = 105, 
                               orgUnit_ids = orgUnit_ids, token = DHIS_TOKEN, dryRun = False)
resp = delete_historic_climate(base_url = DHIS_URL, dataElement = "pridec_climate_mndwi", delete_months = 105, 
                               orgUnit_ids = orgUnit_ids, token = DHIS_TOKEN, dryRun = False)
resp = delete_historic_climate(base_url = DHIS_URL, dataElement = "pridec_climate_gao", delete_months = 105, 
                               orgUnit_ids = orgUnit_ids, token = DHIS_TOKEN, dryRun = False)
resp.json().get("message")

#sen2_s2 begins 201804
sen2_json = fetch_sen2_climate(orgUnit = orgUnit, months_prior=80)