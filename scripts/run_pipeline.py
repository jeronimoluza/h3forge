import h3forge
region = h3forge.utils.load_wkt(
    # "POLYGON((-58.519638 -34.549585, -58.484587 -34.549585, -58.484587 -34.572794, -58.519638 -34.572794, -58.519638 -34.549585))"
    "POLYGON((-58.521952 -34.549793, -58.487812 -34.549793, -58.487812 -34.568679, -58.521952 -34.568679, -58.521952 -34.549793))"
)
start_date = "2020-01-01"
end_date = "2020-03-01"
cloud_cover = 0.2

ndvi_array = h3forge.download.sentinel2.get_ndvi(
    region=region,
    start_date=start_date,
    end_date=end_date,
    cloud_cover=cloud_cover,
)


vectors = h3forge.preprocess.vectorize(ndvi_array, region=region)

hexes = h3forge.features.vector_to_h3(vectors, region=region, resolution=10)

h3_agg = h3forge.features.h3_aggregation(
    hexes, region=region, resolution=8, time_agg='daily', strategy='mean'
)

print(h3_agg)
