import envineq

region = envineq.utils.load_wkt(
    "POLYGON((5.9559 47.8084, 10.4921 47.8084, 10.4921 45.818, 5.9559 45.818, 5.9559 47.8084))"
)
start_date = "2020-01-01"
end_date = "2020-01-31"
cloud_cover = 0.2

ndvi_layers = envineq.download.ndvi.sentinel2.get_data(
    region=region,
    start_date=start_date,
    end_date=end_date,
    cloud_cover=cloud_cover,
)
