from pridec_gee import get_dhis_geojson



def test_get_dhis_geojson():

    #uses demo instance
    dhis_url = "https://play.im.dhis2.org/stable-2-40-11/"
    user = "admin"
    pwd = "district"

    get_dhis_geojson(parent_ou= "Vth0fbpFcsO",
                     ou_level="3",
                     dhis_url = dhis_url,
                     dhis_user = user,
                     dhis_pwd = pwd)
    