import xarray as xr

def calculate_ndvi(bands_dataset: xr.Dataset) -> xr.DataArray:
    """
    Calculates the Normalized Difference Vegetation Index (NDVI).

    NDVI = (NIR - Red) / (NIR + Red)

    Args:
        bands_dataset (xr.Dataset): An xarray Dataset containing 'nir' and 'red' bands
                                    as DataArrays. These are typically loaded by the
                                    Sentinel2Connector.

    Returns:
        xr.DataArray: An xarray DataArray containing the calculated NDVI values.
                      The DataArray will have the same coordinates and dimensions
                      as the input bands (e.g., time, y, x).
    """
    if not isinstance(bands_dataset, xr.Dataset):
        raise TypeError("Input 'bands_dataset' must be an xarray.Dataset.")

    if "nir" not in bands_dataset:
        raise ValueError("Dataset must contain 'nir' band for NDVI calculation.")
    if "red" not in bands_dataset:
        raise ValueError("Dataset must contain 'red' band for NDVI calculation.")

    nir_band = bands_dataset["nir"]
    red_band = bands_dataset["red"]

    # Add a small epsilon to the denominator to prevent division by zero errors
    # where (nir + red) might be zero (e.g., water bodies, no data).
    epsilon = 1e-8 
    ndvi = (nir_band - red_band) / (nir_band + red_band + epsilon)
    
    # Name the DataArray
    ndvi.name = "ndvi"
    
    # NDVI values should be between -1 and 1. 
    # Optionally, clip values to this range if necessary, though typically not required with epsilon.
    # ndvi = ndvi.clip(-1, 1)

    return ndvi

# Placeholder for other potential band transformations in the future
# def calculate_ndwi(bands_dataset: xr.Dataset) -> xr.DataArray:
#     # Example: NDWI = (Green - NIR) / (Green + NIR)
#     if "green" not in bands_dataset or "nir" not in bands_dataset:
#         raise ValueError("Dataset must contain 'green' and 'nir' bands for NDWI.")
#     green_band = bands_dataset["green"]
#     nir_band = bands_dataset["nir"]
#     epsilon = 1e-8
#     ndwi = (green_band - nir_band) / (green_band + nir_band + epsilon)
#     ndwi.name = "ndwi"
#     return ndwi