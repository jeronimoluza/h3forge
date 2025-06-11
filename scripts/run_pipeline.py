import envineq
region = envineq.utils.load_wkt(
    "POLYGON((-58.519638 -34.549585, -58.484587 -34.549585, -58.484587 -34.572794, -58.519638 -34.572794, -58.519638 -34.549585))"
)
start_date = "2020-01-01"
end_date = "2020-03-01"
cloud_cover = 0.2

ndvi_array = envineq.download.sentinel2.get_ndvi(
    region=region,
    start_date=start_date,
    end_date=end_date,
    cloud_cover=cloud_cover,
)


vectors = envineq.preprocess.vectorize(ndvi_array, region=region)