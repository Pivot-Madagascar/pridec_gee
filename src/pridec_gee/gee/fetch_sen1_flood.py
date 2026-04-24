import ee
import pandas as pd
from numpy import nan as np_nan


from .s1_ard.wrapper import s1_preproc
from .s1_ard.helper import add_ratio_lin, lin_to_db2

def fetch_sen1_flood(
    rice_features: ee.FeatureCollection,
    date_range: dict[str, str],
    test_run: bool = True,
):
    """Extract Ricefield flooding proportion from Sentinel-1 data. This function is specific to ricefield data from Ifanadiana district (Pivot).

    This function is designed for ricefield data from Ifanadiana district (Pivot),
    extracting flooding information for each rice field.
    Outputs a JSON-ready list formatted for DHIS2 import.

    Args:
        rice_features: FeatureCollection of rice fields. Must include:
            - `id`: unique identifier for each rice field
            - `orgUnit`: DHIS2 organisation unit to aggregate values to
        date_range: Dictionary with start and end dates:
            - 'start_date_gee': start date as YYYY-MM-DD
            - 'end_date_gee': end date as YYYY-MM-DD
        test_run: If True, performs a test using only a small subset of images (default True).

    Returns:
        pandas dataframe with columns:
            - 'orgUnit': organization unit ID
            - 'period': period of observation (YYYYMM)
            - 'value': climate value (e.g., temperature, precipitation)
            - 'dataElement': corresponding DHIS2 data element code (pridec_climate_*)
        Can be turned into a DHIS2 formatted json file with:
                df_dict = {
                    "dataValues": df_long.to_dict(orient="records")
                }
    """

    geom = rice_features
    rice_area = geom.map(
        lambda f: f.set("area", f.geometry().area())
    )

    # bbox = ee.Geometry.Rectangle([46,-23,49.5,-19], 'EPSG:4326')
    bbox = geom.bounds()

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
        "FORMAT": 'LINEAR',
        "CLIP_TO_ROI": False,
        "SAVE_ASSET": False,
        "ASSET_ID": "asset_id"
    }

    #preprocess sen1 and output db values
    s1_preprocessed = s1_preproc(fxparams)
    s1_processed = s1_preprocessed.map(add_ratio_lin).map(lin_to_db2)

    # Threshold based on Randriamihaja et al. 2025 (doi:10.1186/s12936-025-05344-3)
    def threshold_flood(image):
        flood = image.select('VH').lte(-15.9279).rename('floodProp').uint8()
        return flood.set('date', image.date().format('YYYY-MM-dd'))
    
    
        #extract mean to each rice field
    def reduce_by_regions(image):
        return image.select('floodProp').reduceRegions(
            collection=rice_area,
            reducer=ee.Reducer.mean(),
            scale=10
        ).map(lambda f: f.set('date', image.get('date')).setGeometry(None))
    
    def format_feature(feature):
        return ee.Feature(None, {
            'orgUnit': feature.getString('orgUnit'),
            'rice_id': feature.getString('id'),
            'date': feature.getString('date'),
            'floodProp': feature.get('mean'),
            'rice_area': feature.get('area')}
        )
    
    image_flood = s1_processed.map(threshold_flood)
    if test_run:
        image_list = image_flood.limit(3).toList(3)  #for testing
    else:
        image_list = image_flood.toList(image_flood.size())

    n_image = image_list.size().getInfo()
    dfs = []

    print(f"Extracting flood data for {n_image} images.")
    
    for i in range(n_image):
        this_image = ee.Image(image_list.get(i))

        reduced = reduce_by_regions(this_image)
        formatted = reduced.map(format_feature)

        try:
            features = formatted.getInfo()["features"]
            properties = [f["properties"] for f in features]
            df = pd.DataFrame(properties)
            df["floodProp"] = pd.to_numeric(df["floodProp"], errors="coerce").fillna(0)
            dfs.append(df)
        except Exception as e:
            print(f"Skipping image {i} due to error: {e}")
            continue

    df_all = pd.concat(dfs, ignore_index=True)
    df_all["date"] = pd.to_datetime(df_all["date"])
    df_all["period"] = df_all["date"].dt.strftime("%Y%m")

    flood_df = (
        df_all.set_index(["orgUnit", "period"])
        .groupby(["orgUnit", "period"])
        .apply(lambda g: (g["floodProp"] * g["rice_area"]).sum() / g["rice_area"].sum())
        .rename("pridec_climate_floodedRice")
        .reset_index()
    )

    df_long = flood_df.melt(
        id_vars=['orgUnit', 'period'],
        var_name='dataElement',
        value_name='value'
    )

    df_long["value"] = df_long["value"].where(df_long["value"].between(0, 1), np_nan)
    #drop missing, round, and change period to string
    df_long = df_long.dropna(subset=['value'])
    df_long['value'] = df_long['value'].round(6)
    df_long['period'] = df_long['period'].astype(str)
    df_long["value"] = pd.to_numeric(df_long["value"], errors='coerce')

    df_long = df_long.reset_index(drop=True)

    return df_long