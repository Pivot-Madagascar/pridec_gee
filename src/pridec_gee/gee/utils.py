import ee

## Function to extract monthly values from an imageCollection of rasters to spatial polygons
## Spatial mean is used by default, but temporally aggregation can be chosen via parameters
## ic: imageCollection of rasters to extract from
## fc: featureCollection of spatial polygons
## start_date: start date of period to extract
## end_date: last date of period to extract
## params: parameters for extraction, potential values are reducer, bands, and bandsRename
def month_agg_sp_mean(ic, fc, start_date, end_date, params=None):
    # Initialize internal params dictionary with default values.
    _params = {
        'reducer': ee.Reducer.mean(),
        'bands': None,
        'bandsRename': None
    }
    
    # Replace initialized params with provided params.
    if params:
        for param in params:
            _params[param] = params.get(param, _params[param])
    
    # Set default parameters based on an image representative.
    img_rep = ic.first()
    default_scale = img_rep.select([0]).projection().nominalScale().getInfo()

    # Create list of dates that we would like to loop over
    first_day_date = ee.Date(start_date)
    last_day_date = ee.Date(end_date)


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
                         .select(_params['bands'], _params['bandsRename'])
        
        reduce_step = filter_step.reduce(  # Apply reducer
            reducer=_params['reducer']
        ).set('system:time_start', start_date.millis()) \
         .set('year_month', start_date.format("YYYYMM"))

        return ee.Image(reduce_step)
    
    # Map over the list of dates and create monthly aggregated image collection
    ic_month = ee.ImageCollection(dates.map(month_func).flatten())

    # Function for calculating spatial mean by region
    def calc_spatial_mean(image):
        # Reduce the image by regions
        reduced = image.reduceRegions(
            collection=fc,
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
    results = [feature['properties'] for feature in results_data]

    return results




## Function to extract values from an imageCollection of rasters to a spatial polygon
## ic: imageCollection of rasters to extract from
## fc: featureCollection of spatial polygons
##params: optional object that provides function arguments

##from https://google-earth-engine.com/Vectors-and-Tables/Zonal-Statistics/
def zonal_stats(ic, fc, params = None):

# Initialize internal params dictionary with default values.
    _params = {
        'reducer': ee.Reducer.mean(),
        'scale': None,
        'crs': None,
        'bands': None,
        'bandsRename': None,
        'imgProps': None,
        'imgPropsRename': None,
        'datetimeName': 'datetime',
        'datetimeFormat': 'YYYY-MM-dd HH:mm:ss'
    }

    # Replace initialized params with provided params (if any).
    if params:
        for param in params:
            _params[param] = params.get(param, _params[param])

    # Set default parameters based on representative image
    imgRep = ic.first()
    nonSystemImgProps = ee.Feature(None).copyProperties(imgRep).propertyNames()

               # Set default parameters based on the representative image.
    if not _params['bands']:
        _params['bands'] = imgRep.bandNames()
    if not _params['bandsRename']:
        _params['bandsRename'] = _params['bands']
    if not _params['imgProps']:
        _params['imgProps'] = nonSystemImgProps
    if not _params['imgPropsRename']:
        _params['imgPropsRename'] = _params['imgProps']

    # Map the reduceRegions function over the image collection.
    def process_image(img):
        # Select bands (optionally rename) and set datetime & timestamp properties.
        img = img.select(_params['bands'], _params['bandsRename']) \
               .set(_params['datetimeName'], img.date().format(_params['datetimeFormat'])) \
               .set('timestamp', img.get('system:time_start'))
        
        # Define final image property dictionary to set in output features.
        propsFrom = ee.List(_params['imgProps']).cat(ee.List([_params['datetimeName'], 'timestamp']))
        propsTo = ee.List(_params['imgPropsRename']).cat(ee.List([_params['datetimeName'], 'timestamp']))
        imgProps = img.toDictionary(propsFrom).rename(propsFrom, propsTo)

        # Subset points that intersect the given image.
        fcSub = fc.filterBounds(img.geometry())

        # Reduce the image by regions.
        reduced = img.reduceRegions(
            collection=fcSub,
            reducer=_params['reducer'],
            scale=_params['scale'],
            crs=_params['crs']
        )

        # Add metadata to each feature.
        return reduced.map(lambda f: f.set(imgProps))

    # Apply the process_image function to each image in the image collection and flatten results.
    results = ic.map(process_image).flatten()

    return results

## Function to mask clouds from a Sentinel-2 image
def mask_s2_clouds(image):
    qa = image.select('QA60')

    # Bits 10 and 11 are clouds and cirrus, respectively.
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0) \
           .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    
    #mask image and rescale using 10000
    masked_image = image.updateMask(mask).divide(10000)
    masked_image = masked_image.copyProperties(image, ['system:time_start'])

    return masked_image

## Function to add EVI to a Sentinel-2 image
def add_evi(image):
    # Calculate EVI using the formula
    EVI = image.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
            'NIR': image.select('B8'),
            'RED': image.select('B4'),
            'BLUE': image.select('B2')
        }).rename('EVI')
    
    # Add the EVI band to the image
    return image.addBands(EVI)

## Function to add MNDWI (normalized water index) to a Sentinel-2 image
def add_mndwi(image):
    # Calculate index using the formula
    MNDWI = image.expression(
        '(GREEN - NIR) / (GREEN + NIR)', {
            'GREEN' : image.select('B3'),
            'NIR'   : image.select('B8')
        }).rename('MNDWI')
    
    # Add the band to the image
    return image.addBands(MNDWI)

## Function to add NDWIGAO (normalized moisture index) to a Sentinel-2 image
def add_gao(image):
    # Calculate index using the formula
    GAO = image.expression(
        '(NIR - SWIR) / (NIR + SWIR)',
        {
            'SWIR': image.select('B11'),
            'NIR' : image.select('B8')
        }
    ).rename('GAO')
    
    return image.addBands(GAO)

# Function to add RH to a ERA5 image. Note that temperatures must be celcius
def add_rh(image):
    # Calculate index using the formula
    RH = image.expression(
        '100.0 * (2.71828 ** (((243.04 * 16.625) * (TD - T))/((243.04 + T) * (243.04 + TD))))', {
            'T'  : image.select('temp_c'),
            'TD' : image.select('dewtemp_c')
        }).rename('RH')
    
    # Add the band to the image
    return image.addBands(RH)

## Function to convert ERA5 temperature to celsius
def add_tempC(image):
    temp_c = image.expression(
        'T - 273.15', {
      'T' : image.select('temperature_2m')
    }).rename("temp_c")

    return image.addBands(temp_c)

## Function to convert ERA5 dew point temperature to celsius
def add_dewtempC(image):
    dewtemp_c = image.expression(
        'T - 273.15', {
      'T' : image.select('dewpoint_temperature_2m')
    }).rename("dewtemp_c")

    return image.addBands(dewtemp_c)

#validate provided variables
def validate_variables(input_vars, allowed_vars):
    invalid = set(input_vars) - set(allowed_vars)
    if invalid:
        raise ValueError(
            f"Invalid variables specified: {sorted(invalid)}"
            f"Allowed variables: {sorted(allowed_vars)}"
        )


