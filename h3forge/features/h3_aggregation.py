import geopandas as gpd
import pandas as pd
import numpy as np
import h3
from shapely.geometry import Polygon
from datetime import datetime


def h3_aggregation(hexes, region=None, resolution=8, time_agg=None, strategy='mean', include_geometry=False):
    """
    Aggregates H3 hexagons to a coarser resolution and optionally by time periods.
    
    Parameters
    ----------
    hexes : geopandas.GeoDataFrame
        Input GeoDataFrame with H3 hexagons. Must have a 'hex' column with H3 cell IDs.
        If time aggregation is requested, must also have a 'date' column.
    region : shapely.geometry.Polygon, optional
        Region to filter the results by. Only hexagons that intersect with this region will be included.
    resolution : int, default 8
        Target H3 resolution to aggregate to. Must be coarser (lower number) than the input hexagons.
    time_agg : str, optional
        Time aggregation strategy. Options are:
        - 'daily': Aggregate by day
        - 'monthly': Aggregate by month
        - 'yearly': Aggregate by year
        - None: No time aggregation (default)
    strategy : str, default 'mean'
        Aggregation strategy for numeric values. Options are:
        - 'mean': Average of child hexagons
        - 'sum': Sum of child hexagons
        - 'min': Minimum value of child hexagons
        - 'max': Maximum value of child hexagons
    include_geometry : bool, default False
        Whether to include the H3 hexagon geometry in the output GeoDataFrame
        
    Returns
    -------
    geopandas.GeoDataFrame
        Aggregated GeoDataFrame with H3 hexagons at the target resolution
    """
    if hexes is None or len(hexes) == 0:
        return gpd.GeoDataFrame()
    
    # Make a copy to avoid modifying the input
    df = hexes.copy()
    
    # Check if 'hex' column exists
    if 'hex' not in df.columns:
        raise ValueError("Input GeoDataFrame must have a 'hex' column with H3 cell IDs")
    
    # Check if time aggregation is requested but 'date' column is missing
    if time_agg is not None and 'date' not in df.columns:
        raise ValueError("Time aggregation requested but 'date' column is missing in input GeoDataFrame")
    
    # Add parent hex column at the target resolution
    df['parent_hex'] = df['hex'].apply(lambda h: h3.cell_to_parent(h, resolution))
    
    # Prepare for time aggregation if requested
    if time_agg is not None:
        # Convert date strings to datetime objects
        df['datetime'] = pd.to_datetime(df['date'])
        
        # Create time aggregation column based on the requested strategy
        if time_agg == 'daily':
            df['time_group'] = df['datetime'].dt.strftime('%Y-%m-%d')
        elif time_agg == 'monthly':
            df['time_group'] = df['datetime'].dt.strftime('%Y-%m')
        elif time_agg == 'yearly':
            df['time_group'] = df['datetime'].dt.strftime('%Y')
        else:
            raise ValueError(f"Invalid time_agg value: {time_agg}. Must be 'daily', 'monthly', 'yearly', or None")
        
        # Group by parent hex and time group
        group_cols = ['parent_hex', 'time_group']
    else:
        # Group only by parent hex
        group_cols = ['parent_hex','date']
    
    # Identify numeric columns for aggregation (excluding geometry, hex, parent_hex, date, etc.)
    exclude_cols = ['geometry', 'hex', 'parent_hex', 'date', 'datetime', 'time_group']
    numeric_cols = [col for col in df.columns if col not in exclude_cols and 
                   pd.api.types.is_numeric_dtype(df[col])]
    
    if not numeric_cols:
        # If no numeric columns, just group by parent hex (and time if applicable)
        # and count the number of child hexes
        agg_dict = {'hex': 'count'}
        agg_df = df.groupby(group_cols).agg(agg_dict).reset_index()
        agg_df.rename(columns={'hex': 'count'}, inplace=True)
    else:
        # Create aggregation dictionary based on the strategy
        agg_dict = {}
        for col in numeric_cols:
            agg_dict[col] = strategy
        
        # Add count of child hexes
        agg_dict['hex'] = 'count'
        
        # Perform aggregation
        agg_df = df.groupby(group_cols).agg(agg_dict).reset_index()
        agg_df.rename(columns={'hex': 'count'}, inplace=True)
    
    # Rename the parent_hex column to hex
    agg_df.rename(columns={'parent_hex': 'hex'}, inplace=True)
    
    # Add geometry if requested
    if include_geometry:
        # Create geometry for each hex
        def hex_to_polygon(h):
            h3_boundary = h3.cell_to_boundary(h)
            # Swap lat/lng to lng/lat for shapely
            h3_boundary = [(y, x) for x, y in h3_boundary]
            return Polygon(h3_boundary)
        
        agg_df['geometry'] = agg_df['hex'].apply(hex_to_polygon)
        result_gdf = gpd.GeoDataFrame(agg_df, geometry='geometry', crs="EPSG:4326")
    else:
        # Create GeoDataFrame without geometries
        result_gdf = gpd.GeoDataFrame(agg_df)
    
    # Filter by region if provided and geometries are included
    if region is not None and include_geometry:
        result_gdf = result_gdf[result_gdf.intersects(region)]
    
    # Restore date column from time_group if time aggregation was performed
    if time_agg is not None:
        result_gdf.rename(columns={'time_group': 'date'}, inplace=True)
        result_gdf['date'] = pd.to_datetime(result_gdf['date']).dt.strftime('%Y-%m-%d')
    
    print(result_gdf)
    # Sort by hex and date
    result_gdf.sort_values(by=['date', 'hex'], inplace=True)
    
    return result_gdf