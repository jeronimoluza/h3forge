import geopandas as gpd
import xarray as xr
import pandas as pd
import numpy as np
from geocube.vector import vectorize as geocube_vectorize
from shapely.geometry import Polygon, MultiPolygon

def vectorize(xarray_dataset: xr.Dataset, region: gpd.GeoDataFrame|Polygon|MultiPolygon, clip=False) -> gpd.GeoDataFrame:
    """
    Converts a raster dataset to a vectorized GeoDataFrame.
    If the xarray_dataset has a 'time' dimension, the date information will be included in the output GeoDataFrame.
    
    Args:
        xarray_dataset (xr.Dataset): The input raster dataset.
        region (gpd.GeoDataFrame|Polygon|MultiPolygon): The region of interest.
        clip (bool, optional): Whether to clip the vectors to the region. Defaults to False.
    
    Returns:
        gpd.GeoDataFrame: The vectorized GeoDataFrame with date information if available.
    """
    # Check if the dataset has a time dimension
    has_time_dim = 'time' in xarray_dataset.dims
    
    if has_time_dim:
        # Get the time values
        time_values = xarray_dataset.time.values
        all_vectors = []
        
        # Process each time slice
        for time_val in time_values:
            # Extract the dataset for this time
            time_slice = xarray_dataset.sel(time=time_val)
            
            # Vectorize this time slice
            vectors = geocube_vectorize(time_slice).to_crs("EPSG:4326")
            
            # Filter by region
            vectors = vectors[vectors.intersects(region)]
            
            # Clip if requested
            if clip:
                vectors = vectors.clip(region.union_all())
            
            # Add the date information
            if len(vectors) > 0:
                # Convert numpy datetime64 to pandas datetime for better compatibility
                date_str = pd.to_datetime(time_val).strftime('%Y-%m-%d %H:%M:%S')
                vectors['date'] = date_str
                all_vectors.append(vectors)
        
        # Combine all time slices
        if all_vectors:
            vectors = pd.concat(all_vectors, ignore_index=True)
        else:
            # Return empty GeoDataFrame with date column
            vectors = gpd.GeoDataFrame(columns=['date', 'geometry'])
    else:
        # Original behavior for datasets without time dimension
        vectors = geocube_vectorize(xarray_dataset).to_crs("EPSG:4326")
        vectors = vectors[vectors.intersects(region)]
        if clip:
            vectors = vectors.clip(region.union_all())
    
    return vectors