# testing --------------------------------------
    image_to_save = s1_processed.first().select('VH')

    task = ee.batch.Export.image.toAsset(
        image=image_to_save,
        description='exported_sen1',
        assetId='users/mevans/flood_image_20231207_2',
        region=ee.Geometry.Rectangle([49,-21,49.5,-20.5]),  # Or use a predefined geometry
        scale=10,
        maxPixels=1e13
    )
    # task.start()

    sampled = image_to_save.sample(
        region=bbox,
        scale=10,              # Pixel resolution (e.g., 10 for Sentinel-1)
        numPixels=100,         # How many pixels to sample
        seed=42,               # Seed for reproducibility (optional)
        geometries=False       # Include coordinates
    ) 
    sampled_dict = sampled.getInfo()
    print(sampled_dict)
    pixel_values = [
        {**f["properties"]}
        for f in sampled_dict["features"]
    ]      
    print(pixel_values)

    #do tehy overlap?
    print(bbox.bounds().getInfo())
    print(image_to_save.geometry().getInfo())
    # end testing stuff =---------------------


OLD STUFF-------------------------------
    results = image_flood.limit(20).map(reduce_by_regions).flatten().map(format_feature)

    features_list = results.getInfo()["features"]
    properties_list = [f["properties"] for f in features_list]
    df = pd.DataFrame(properties_list)

    df["floodProp"] = pd.to_numeric(df["floodProp"], errors="coerce").fillna(0)

    df = pd.d

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