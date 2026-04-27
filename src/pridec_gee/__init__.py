import logging

from .gee.calc_date_range import calc_date_range
from .gee.fetch_era5_climate import fetch_era5_climate
from .gee.fetch_fewsnet_windspeed import fetch_fewsnet_windspeed
from .gee.fetch_modis_aod import fetch_modis_aod
from .gee.fetch_modis_fire import fetch_modis_fire
from .gee.fetch_sen2_indicators import fetch_sen2_indicators
from .gee.fetch_sen1_flood import fetch_sen1_flood
from .gee.variables import AVAILABLE_VARIABLES

from .dhis2.get_pridec_elements import get_pridec_elements
from .dhis2.get_dhis_geojson import get_dhis_geojson
from .dhis2.delete_historic_climate import delete_historic_climate
from .dhis2.post_climate import post_climate

from .import_pridec_climate import import_pridec_climate
from .fetch_climate_gee import fetch_climate_gee


__all__ = [
    "calc_date_range",
    "fetch_era5_climate",
    "fetch_fewsnet_windspeed",
    "fetch_modis_aod",
    "fetch_modis_fire",
    "fetch_sen2_indicators",
    "fetch_sen1_flood",
    "get_pridec_elements",
    "get_dhis_geojson",
    "delete_historic_climate",
    "post_climate",
    "import_pridec_climate",
    "fetch_climate_gee",
    AVAILABLE_VARIABLES
    ]

package_logger = logging.getLogger(__name__)