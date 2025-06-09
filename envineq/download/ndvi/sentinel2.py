import pystac_client
from odc.stac import configure_rio, load
import dask.distributed
import os

# from shapely.geometry import mapping # Required if region needs conversion via mapping()

# --- Environment Configuration ---
# IMPORTANT: Hardcoding credentials is a security risk.
# Consider using environment variables set outside the script or a secure secrets management system.
os.environ["GDAL_HTTP_TCP_KEEPALIVE"] = "YES"
os.environ["AWS_S3_ENDPOINT"] = "eodata.dataspace.copernicus.eu"
# Ensure these are set in your environment or replace placeholders securely
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv(
    "AWS_ACCESS_KEY_ID", "your_access_key"
)  # ! Fallback for clarity
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv(
    "AWS_SECRET_ACCESS_KEY", "your_secret_access_key"
)  # ! Fallback for clarity
os.environ["AWS_HTTPS"] = "YES"
os.environ["AWS_VIRTUAL_HOSTING"] = "FALSE"
os.environ["GDAL_HTTP_UNSAFESSL"] = (
    "YES"  # Note: Unsafe SSL might be needed for some endpoints but use with caution
)
os.environ["AWS_NO_SIGN_REQUEST"] = "YES"


# --- STAC API Configuration ---
COPERNICUS_STAC_URL = "https://earth-search.aws.element84.com/v1/"


def get_data(region, start_date: str, end_date: str, cloud_cover: float):
    """
    Downloads Sentinel-2 L2A data for a given region and time period,
    calculates NDVI, and returns it as an xarray.DataArray.

    Args:
        region: A GeoJSON-like dictionary or an object with __geo_interface__ (e.g., Shapely geometry)
                representing the area of interest.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        cloud_cover (float): Maximum cloud cover percentage (0-100).

    Returns:
        xarray.DataArray: NDVI data for the specified region and time.
    """
    bbox = region.bounds
    catalog = pystac_client.Client.open(COPERNICUS_STAC_URL)

    filter_query = {
        "eo:cloud_cover": {
            "lte": cloud_cover
        }
    }
    query = catalog.search(
        collections=["sentinel-2-l2a"],
        datetime=f"{start_date}/{end_date}",
        limit=100,
        bbox=bbox,
        query=filter_query
    )


    items = list(query.items())
    print(f"Found: {len(items):d} datasets")
    return items

    data_stack = load(
        items,
        bands=("red", "nir"),
        # crs=crs,
        resolution=10,
        chunks={},  # <-- use Dask
        groupby="solar_day",
    )
    data_stack = data_stack.rio.clip([region], crs=f"EPSG:4326") # Assumes geom_filter is GeoJSON

    # Select NIR and Red bands for NDVI calculation
    # Sentinel-2 bands: B04 is Red, B08 is NIR (both at 10m resolution)
    nir_band = data_stack.get("nir")
    red_band = data_stack.get("red")

    # Calculate NDVI: (NIR - Red) / (NIR + Red)
    ndvi = (nir_band - red_band) / (nir_band + red_band)
    # ndvi = ndvi.rio.write_crs(data_stack.rio.crs)  # Ensure CRS is set


    return ndvi, red_band, nir_band
