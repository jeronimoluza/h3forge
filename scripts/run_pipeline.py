import envineq
from geocube.vector import vectorize
region = envineq.utils.load_wkt(
    "POLYGON((-58.531448 -34.526553, -58.335143 -34.526553, -58.335143 -34.705815, -58.531448 -34.705815, -58.531448 -34.526553))"
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

# computed = ndvi_array.compute()
