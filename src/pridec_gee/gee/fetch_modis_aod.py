import ee
import pandas as pd

from .utils import month_agg_sp_mean

def fetch_modis_aod(orgUnit, date_range):
    """
    Extracts mean Aerosol Optical Depth from MODIS satellite by month for orgUnits from DHIS2

    Args:
        orgUnit (ee.FeatureCollection):     orgUnit polygons to use for extraction. If None, will get from DHIS2 instance
        date_range (list):                   range of dates to download data of. 
                                                Format is a string (start_date_gee[%Y-%m-%d], end_date_gee[%Y-%m-%d]) 

    Returns:
        JSON file with columns orgUnit, period, value, dataElement formatted to submit to DHIS2
    """

    ic = ee.ImageCollection("MODIS/061/MCD19A2_GRANULES").filterBounds(orgUnit)
    ic_mask = ic.map(apply_qa_mask) 

    fxparams = {
    'reducer': ee.Reducer.mean(),  
    'bands': ['Optical_Depth_047',],  
    'bandsRename': ['AOD47']  
    }

    result = month_agg_sp_mean(ic_mask, orgUnit, date_range['start_date_gee'], date_range['end_date_gee'], fxparams)

    #reformat for DHIS2
    df = pd.DataFrame(result)
    #rename to PRIDE-C dhis2 code
    df = df.rename(columns={'mean': 'pridec_climate_AOD'})

    df_long = df.melt(
        id_vars=['orgUnit', 'period'],
        var_name='dataElement',
        value_name='value'
    )
    #drop missing, round, and change period to string
    df_long = df_long.dropna(subset=['value'])
    df_long['value'] = df_long['value'].round(4)
    df_long['period'] = df_long['period'].astype(str)

    #turn into a json file
    df_dict = {
        "dataValues": df_long.to_dict(orient="records")
    }

    return df_dict

def bitwise_extract(input_value, from_bit, to_bit):
    """
    Extracts bits from a number or image using bitwise operations.

    Args:
        input_value (ee.Number or ee.Image): Input to extract bits from.
        from_bit (int): Starting bit position.
        to_bit (int): Ending bit position.

    Returns:
        ee.Number or ee.Image: The extracted bits.
    """
    mask_size = ee.Number(1).add(to_bit).subtract(from_bit)
    mask = ee.Number(1).leftShift(mask_size).subtract(1)
    return input_value.rightShift(from_bit).bitwiseAnd(mask)

def apply_qa_mask(image):
    """
    Applies a QA bitmask to an AOD image, keeping only pixels with QA <= 4.

    Args:
        image (ee.Image): MODIS AOD image with 'Optical_Depth_047' and 'AOD_QA' bands.

    Returns:
        ee.Image: Masked 'Optical_Depth_047' band.
    """
    aod_depth = image.select('Optical_Depth_047')
    qc_aod = image.select('AOD_QA')
    qa_mask = bitwise_extract(qc_aod, 8, 11).lte(4)
    return aod_depth.updateMask(qa_mask)