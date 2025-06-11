import geopandas as gpd
import xarray as xr
from geocube.vector import vectorize as geocube_vectorize
from shapely.geometry import Polygon, MultiPolygon

def vectorize(xarray_dataset: xr.Dataset, region: gpd.GeoDataFrame|Polygon|MultiPolygon, clip=False) -> gpd.GeoDataFrame:
    """
    Converts a raster dataset to a vectorized GeoDataFrame.
    
    Args:
        xarray_dataset (xr.Dataset): The input raster dataset.
        region (gpd.GeoDataFrame|Polygon|MultiPolygon): The region of interest.
        clip (bool, optional): Whether to clip the vectors to the region. Defaults to False.
    
    Returns:
        gpd.GeoDataFrame: The vectorized GeoDataFrame.
    """
    vectors = geocube_vectorize(xarray_dataset).to_crs("EPSG:4326")
    vectors = vectors[vectors.intersects(region)]
    if clip:
        vectors = vectors.clip(region.union_all())
    return vectors