#activate env and install packages first
#source .venv/bin/activate

import ee
import pandas as pd

ee.Authenticate()

ee.Initialize(project='ee-mevans-pridec')

# dem = ee.Image('CGIAR/SRTM90_V4')
# elevation = dem.select('elevation')
# print(elevation.getInfo())

fc = ee.FeatureCollection("projects/ee-pridec/assets/spatial-admin/fkt_polygon")

fews_ic = ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001")
ic = fews_ic.filterBounds(fc)
  
startDate = '2017-01-01'
endDate = '2017-04-01'
_params = {
  'reducer': ee.Reducer.max(),
  'bands': ['Qair_f_tavg', 'Qs_tavg'],
  'bandsRename': ['humidity', 'runoff']
}
   
##Set default parameters based on an image representative.
default_scale = ic.first().select([0]).projection().nominalScale().getInfo()

##create list of dates that we would like to loop over
firstDay = ee.Date(startDate)
lastDay = ee.Date(endDate)
n_months = lastDay.difference(firstDay, 'month')
dateList = ee.List.sequence(0,n_months,1)

def make_date(n):
  return firstDay.advance(n, 'month')

dates = dateList.map(make_date)
print(dates) #debug
  
##Function to get aggregate for each month based on first day of the month
def month_func(this_date):
    this_date = ee.Date(this_date)
    next_date = this_date.advance(1, 'month') 

    filtered = ic.filterDate(this_date, next_date) \
                 .select(_params['bands'], _params['bandsRename'])
    
    reduced = filtered.reduce(_params['reducer']) \
                      .set('system:time_start', this_date.millis()) \
                      .set('year_month', this_date.format("YYYY'_'MM"))
    
    return reduced

# Apply the monthly reducer
monthly_images = dates.map(lambda d: month_func(d))
monthly_ic = ee.ImageCollection(monthly_images)

# Reduce each image over the feature collection
def reduce_image(img):
    img = ee.Image(img)
    reduced = img.reduceRegions(
        collection=fc,
        reducer=ee.Reducer.mean(),
        scale=default_scale,
        crs='EPSG:4326'
    )
    reduced = reduced.map(lambda f: f.set({
        'year_month': img.get('year_month')
    }).setGeometry(None))
    return reduced

# Map the reduceImage function over the collection
results_fc = monthly_ic.map(reduce_image).flatten()
results_list = results_fc.getInfo()

print(type(results_list))

for i, feature in enumerate(results_list[:5]):
    print(f"Feature {i}:")
    print(feature)  # Print the feature to inspect its structure
    print()


if isinstance(results_list, dict):
    # Extract the list of features from the dictionary
    results_data = results_list.get('features', [])
else:
    # If it's already a list, assign it directly
    results_data = results_list

# Check the type and length of results_data
print(type(results_data))  # It should be a list
print(len(results_data))   # Check how many features we have

# Now, extract the 'properties' from each feature in results_data
properties_data = [feature['properties'] for feature in results_data]

# Convert to DataFrame
df = pd.DataFrame(properties_data)

# Print the first few rows to check
print("\nResults as DataFrame:")
print(df.head())

# Save the DataFrame to a CSV file locally
csv_filename = 'earth_engine_results.csv'
df.to_csv(csv_filename, index=False)

print(f"\nResults saved as {csv_filename}")

# or take this a json and push to dhis2 instance
# will need to be reformatted