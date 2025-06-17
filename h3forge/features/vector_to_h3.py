import geopandas as gpd
import pandas as pd
import numpy as np
import h3
from shapely.geometry import Polygon


def vector_to_h3(gdf, resolution, region=None, include_geometry=False):
    """
    Convert a GeoDataFrame with geometries to a GeoDataFrame of H3 hexagons.
    
    For each input geometry, finds all H3 cells (at the specified resolution) whose
    centroids fall inside that geometry, and replicates the input row's attributes
    for each of these H3 cells.
    
    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        Input GeoDataFrame with geometries
    resolution : int
        H3 resolution to use (0-15)
    region : shapely.geometry.Polygon, optional
        Region to filter the results by
    include_geometry : bool, default False
        Whether to include the H3 hexagon geometry in the output GeoDataFrame
        
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame with H3 hexagons
    """
    if gdf is None or len(gdf) == 0:
        return gpd.GeoDataFrame()
    
    # Create a list to store the results
    h3_rows = []
    
    # Process each row in the input GeoDataFrame
    for _, row in gdf.iterrows():
        geometry = row.geometry
        
        # Skip invalid geometries
        if geometry is None or not geometry.is_valid:
            continue
        
        # Convert the geometry to H3 cells
        try:
            # Use h3.geo_to_cells to get all H3 cells that have their centroid inside the geometry
            h3_cells = h3.geo_to_cells(geometry.__geo_interface__, resolution)
            
            if not h3_cells:
                continue
                
            # Create a new row for each H3 cell
            for h3_cell in h3_cells:
                # Create a copy of the original row's attributes
                new_row = row.drop('geometry').copy()
                
                # Add the H3 cell ID
                new_row['hex'] = h3_cell
                
                # Add the H3 cell geometry if requested
                if include_geometry:
                    # Convert H3 cell to polygon geometry
                    h3_boundary = h3.cell_to_boundary(h3_cell)
                    h3_boundary = [(y,x) for x,y in h3_boundary]
                    h3_polygon = Polygon(h3_boundary)
                    new_row['geometry'] = h3_polygon
                
                h3_rows.append(new_row)
                
        except Exception as e:
            # Skip problematic geometries
            print(f"Error processing geometry: {e}")
            continue
    
    # If no valid H3 cells were found, return an empty GeoDataFrame
    if not h3_rows:
        return gpd.GeoDataFrame()
    
    # Create a new GeoDataFrame from the results
    result_df = pd.DataFrame(h3_rows)
    
    # Convert to GeoDataFrame if geometries are included
    if include_geometry:
        result_gdf = gpd.GeoDataFrame(result_df, geometry='geometry')
    else:
        # Create a GeoDataFrame without geometries
        result_gdf = gpd.GeoDataFrame(result_df)
    
    # Filter by region if provided
    if region is not None and include_geometry:
        result_gdf = result_gdf[result_gdf.intersects(region)]
    
    return result_gdf