import ee
import pandas as pd

def fetch_modis_fire(orgUnit, date_range):
    """
    Extracts proportion of land with active fire during a month from MODIS satellite for orgUnits from DHIS2

    Args:
        orgUnit (ee.FeatureCollection): orgUnit polygons to use for extraction. If None, will get from DHIS2 instance
        date_range (dict): range of dates to download data of. 
                    Format is a string (start_label [%Y%m], end_label[%Y%m], start_date_gee[%Y-%m-%d], end_date_gee[%Y-%m-%d])

    Returns:
        JSON file with columns orgUnit, period, value, dataElement formatted to submit to DHIS2
    """

    ic = ee.ImageCollection("MODIS/061/MYD14A2").filterBounds(orgUnit)
    #defaut parameters from first image
    img_rep = ic.first()
    default_scale = img_rep.select([0]).projection().nominalScale().getInfo()

        # Create list of dates that we would like to loop over
    first_day_date = ee.Date(date_range['start_date_gee'])
    last_day_date = ee.Date(date_range['end_date_gee'])
    n_months = last_day_date.difference(first_day_date, 'month')
    date_list = ee.List.sequence(0, n_months, 1)

    def make_datelist(n):
        return first_day_date.advance(n, 'month')
    dates = date_list.map(make_datelist)

    # Function to get aggregate for each month based on the first day of the month
    def month_func(this_date):
        start_date = ee.Date(this_date)  # starting date
        end_date = start_date.advance(1, 'month')  # end of month for filter
        filter_step = ic.filter(ee.Filter.date(start_date, end_date)) \
                         .select('FireMask')
        
        #get maximum value for each pixel in Firemask during the month
        reduce_step1 = filter_step.reduce(  
            reducer = ee.Reducer.max()
        )
        #then reclassify to only keep pixels with 7 or greater (low confidence of fire and above)
        reduce_step2 = reduce_step1.gte(7) \
        .set('system:time_start', start_date.millis()).set('year_month', start_date.format("YYYYMM"))

        return ee.Image(reduce_step2)
    
    # Map over the list of dates and create monthly aggregated image collection
    ic_month = ee.ImageCollection(dates.map(month_func).flatten())

    # Function for calculating spatial mean by region. Defined here because map only takes one arg
    def calc_spatial_mean(image):
        # Reduce the image by regions
        reduced = image.reduceRegions(
            collection=orgUnit,
            reducer=ee.Reducer.mean(),  # Spatial mean
            scale=default_scale,
            crs="EPSG:4326"
        )
            
        # Add metadata to each feature
        return reduced.map(lambda f: f.set({
                'period': image.get('year_month')
        }).setGeometry(None))  # Remove geometry to save space
        
    # Apply the spatial mean function to each image in the collection
    results_fc = ic_month.map(calc_spatial_mean).flatten()
    results_list = results_fc.getInfo()
    #to deal with nestedness
    results_data = results_list.get('features', [])
    result = [feature['properties'] for feature in results_data]

    #reformat for DHIS2
    df = pd.DataFrame(result)
    #rename to PRIDE-C dhis2 code
    df = df.rename(columns={'mean': 'pridec_climate_propFire'})

    df_long = df.melt(
        id_vars=['orgUnit', 'period'],
        var_name='dataElement',
        value_name='value'
    )
    #drop missing, round, and change period to string
    df_long = df_long.dropna(subset=['value'])
    df_long['value'] = df_long['value'].round(6)
    df_long['period'] = df_long['period'].astype(str)

    #turn into a json file
    df_dict = {
        "dataValues": df_long.to_dict(orient="records")
    }

    return df_dict

