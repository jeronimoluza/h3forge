import stackstac
import pystack_client
import os

os.environ["GDAL_HTTP_TCP_KEEPALIVE"] = "YES"
os.environ["AWS_S3_ENDPOINT"] = "eodata.dataspace.copernicus.eu"
os.environ["AWS_ACCESS_KEY_ID"] = "your_access_key"  # !
os.environ["AWS_SECRET_ACCESS_KEY"] = "your_secret_access_key"  # !
os.environ["AWS_HTTPS"] = "YES"
os.environ["AWS_VIRTUAL_HOSTING"] = "FALSE"
os.environ["GDAL_HTTP_UNSAFESSL"] = "YES"


URL = "https://stac.dataspace.copernicus.eu/v1"
cat = pystac_client.Client.open(URL)
cat.add_conforms_to("ITEM_SEARCH")

geom = {
    "type": "Polygon",
    "coordinates": [
        [
            [14.254, 50.014],
            [14.587, 50.014],
            [14.587, 50.133],
            [14.254, 50.133],
            [14.254, 50.014],
        ]
    ],
}

params = {
    "max_items": 100,
    "collections": "sentinel-2-l2a",
    "datetime": "2017-06-01/2017-09-30",
    "intersects": geom,
    "query": {"eo:cloud_cover": {"lte": 20}},
    "sortby": "properties.eo:cloud_cover",
    "fields": {"exclude": ["geometry"]},
}

items = list(cat.search(**params).items_as_dicts())

stack = stackstac.stack(
    items=items,
    bounds_latlon=(14.254, 50.014, 14.587, 50.133),
    chunksize=98304,
    epsg=32634,
    gdal_env=stackstac.DEFAULT_GDAL_ENV.updated(
        {
            "GDAL_NUM_THREADS": -1,
            "GDAL_HTTP_UNSAFESSL": "YES",
            "GDAL_HTTP_TCP_KEEPALIVE": "YES",
            "AWS_VIRTUAL_HOSTING": "FALSE",
            "AWS_HTTPS": "YES",
        }
    ),
)

rgb = stack.sel(band=["B04_20m", "B03_20m", "B02_20m"])

nir = stack.sel(band="B08_10m")
red = stack.sel(band="B04_10m")

ndvi = (nir - red) / (nir + red)
