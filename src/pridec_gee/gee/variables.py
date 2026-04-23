from .fetch_era5_climate import ERA5_VARIABLES
from .fetch_fewsnet_windspeed import FEWSNET_VARIABLES
from .fetch_sen2_indicators import  SEN2_VARIABLES

AVAILABLE_VARIABLES = ERA5_VARIABLES + FEWSNET_VARIABLES + SEN2_VARIABLES + ["pridec_climate_AOD", "pridec_climate_propFire", "pridec_climate_floodedRice"]
