import ee
import pandas as pd
import json
from numpy import nan as np_nan

from utils.get_date_range import get_date_range
from utils.gee_s1_ard.wrapper import s1_preproc
from utils.gee_s1_ard.helper import add_ratio_lin, lin_to_db2

def fetch_sen1_flood(Self):
    """
    Extract Ricefield flooding from Sentinel-1 data. Requires access to GEE asset containing major rice fields

    Args:

    Returns:
        json of flooding data formatted for DHIS2 as dataValues
    """
     
    geom = ee.FeatureCollection("projects/ee-mevans-pridec/assets/major-rice") 
    bbox = ee.Geometry.Rectangle([46,-23,49.5,-19])
    date_range =  get_date_range(end_months_ago = 4, end_on_last_day=True, start_months_ago = 8)

    fxparams = {
        # 1. Data selection
        "START_DATE": date_range['start_date_gee'],  # datetime string or ee.Date
        "STOP_DATE": date_range['end_date_gee'],
        "POLARIZATION": 'VVVH',
        "ORBIT": 'DESCENDING',
        "GEOMETRY": geom,  # should be an ee.Geometry or ee.FeatureCollection
        "ROI": bbox,

        # 2. Border noise correction
        "APPLY_BORDER_NOISE_CORRECTION": True,

        # 3. Speckle filtering
        "APPLY_SPECKLE_FILTERING": True,
        "SPECKLE_FILTER_FRAMEWORK": 'MULTI',
        "SPECKLE_FILTER": 'LEE',
        "SPECKLE_FILTER_KERNEL_SIZE": 9,
        "SPECKLE_FILTER_NR_OF_IMAGES": 10,

        # 4. Terrain flattening
        "APPLY_TERRAIN_FLATTENING": True,
        "DEM": ee.Image('USGS/SRTMGL1_003'),
        "TERRAIN_FLATTENING_MODEL": 'VOLUME',
        "TERRAIN_FLATTENING_ADDITIONAL_LAYOVER_SHADOW_BUFFER": 0,

        # 5. Output
        "FORMAT": 'DB',
        "CLIP_TO_ROI": False,
        "SAVE_ASSET": False,
        "ASSET_ID": "asset_id"
    }

    #preprocess sen1 and output db values
    s1_preprocessed = s1_preproc(fxparams)
    s1_processed = s1_preprocessed.map(add_ratio_lin).map(lin_to_db2)

    # Threshold based on Randriamihaja et al. 2025 (doi:10.1186/s12936-025-05344-3)
    def threshold_flood(image):
        flood = image.select('VH').lte(-15.9279).rename('floodProp')
        flood = flood.updateMask(flood)  # explicitly mask out zeros
        flood = flood.uint8()  # Ensure it's numeric for reducers
        return flood.set('date', image.date().format('YYYY-MM-dd'))
    
    
        #extract mean to each rice field
    def reduce_by_regions(image):
        return image.select('floodProp').reduceRegions(
            collection=fxparams["GEOMETRY"],
            reducer=ee.Reducer.mean(),
            scale=10,
            crs='EPSG:4326'
        ).map(lambda f: f.set('date', image.get('date')).setGeometry(None))
    
    def format_feature(feature):
        return ee.Feature(None, {
            'comm_fkt': feature.getString('comm_fkt'),
            'rice_id': feature.getString('id'),
            'date': feature.getString('date'),
            'floodProp': feature.get('mean')
        })
    

    ## STILL NOT WORKING, NOT SURE WHY. MAY BE DUE TO MASKING OR LITERAL MISSING IMAGES
    image_flood = s1_processed.map(threshold_flood)

    sample = image_flood.limit(25)

    sample_result = sample.map(reduce_by_regions).flatten().map(format_feature)
    sample_out = sample_result.toDictionary().getInfo()
    print(sample_out)

    #PAGINATE HER MAYBE?
    results_raw = image_flood.map(reduce_by_regions).flatten()

    

    result = results_raw.map(format_feature)

    # Pull features as a list of dicts (client-side) #THIS TIMES OUT, NEED TO PAGINATE OR EXPORT DIRECTLY
    features_list = result.limit(10).getInfo()['features']

    # Extract properties dict from each feature
    properties_list = [f['properties'] for f in features_list]

    #reformat for DHIS2
    df = pd.DataFrame(properties_list)

    return df
"""
    #drop mean from column names
    df.columns = [col.removesuffix('_mean') if col.endswith('_mean') else col for col in df.columns]

    df_long = df.melt(
        id_vars=['orgUnit', 'period'],
        var_name='dataElement',
        value_name='value'
    )

    #values outisde of -1 to 1 become NA
    df_long["value"] = df_long["value"].where(df_long["value"].between(-1, 1), np_nan)
    #drop missing, round, and change period to string
    df_long = df_long.dropna(subset=['value'])
    df_long['value'] = df_long['value'].round(4)
    df_long['period'] = df_long['period'].astype(str)

    #turn into a json file
    df_dict = {
        "dataValues": df_long.to_dict(orient="records")
    }

    data_json = json.dumps(df_dict, indent=2)

    return data_json
    """