import pystac_client
import xarray as xr
from odc.stac import load

STAC_URL = "https://earth-search.aws.element84.com/v1/"

class Sentinel2Connector:
    """
    Connector class to fetch and load Sentinel-2 STAC data.
    """
    def __init__(self, region, start_date: str, end_date: str, cloud_cover: float):
        """
        Initializes the connector with search parameters.

        Args:
            region: A GeoJSON-like dictionary or an object with __geo_interface__ (e.g., Shapely geometry)
                    representing the area of interest.
            start_date (str): Start date in 'YYYY-MM-DD' format.
            end_date (str): End date in 'YYYY-MM-DD' format.
            cloud_cover (float): Maximum cloud cover percentage (0-100).
        """
        self.region = region
        self.start_date = start_date
        self.end_date = end_date
        self.cloud_cover = cloud_cover
        self.catalog = pystac_client.Client.open(STAC_URL)
        self.items = None
        self._band_properties_cache = {} # Cache for scale/offset factors

    def _search_items(self):
        """Performs the STAC search if items have not been fetched yet."""
        if self.items is not None:
            return

        bbox = self.region.bounds
        filter_query = {"eo:cloud_cover": {"lte": self.cloud_cover}}

        query = self.catalog.search(
            collections=["sentinel-2-l2a"],
            datetime=f"{self.start_date}/{self.end_date}",
            limit=100,  # Consider making this configurable
            bbox=bbox,
            query=filter_query
        )
        self.items = list(query.items())
        print(f"Found: {len(self.items):d} datasets for the query.")

    def load_bands(self, bands_to_load, resolution=10, crs=None, chunks={}):
        """
        Loads specified bands for the searched items.

        Args:
            bands_to_load (tuple or list): List of band names to load (e.g., ('red', 'nir')).
            resolution (int): Spatial resolution in meters.
            crs (str, optional): Target Coordinate Reference System (e.g., "EPSG:4326"). 
                                 If None, uses the CRS of the first item.
            chunks (dict): Dask chunking configuration.

        Returns:
            xarray.Dataset: Loaded bands as a dataset, clipped to the region.
        """
        self._search_items()
        if not self.items:
            print("No items found to load bands from.")
            return None

        data_stack = load(
            self.items,
            bands=bands_to_load,
            resolution=resolution,
            crs=crs,
            chunks=chunks,
            groupby="solar_day", # Groups by day to handle multiple scenes per day if any
            intersects=self.region,
        )
        
        # Manually apply scale and offset factors for each band
        for band_name in data_stack.data_vars:
            if band_name in bands_to_load: # Apply only to requested bands that were loaded
                props = self._get_band_properties(str(band_name))
                scale = props.get('scale', 1.0)
                offset = props.get('offset', 0.0)
                # Ensure band data is float before scaling if it's not already
                # odc.stac.load might return float if dtype isn't specified as int
                data_stack[band_name] = data_stack[band_name].astype(float, copy=False).compute()

        return data_stack

    def _get_band_properties(self, band_name: str) -> dict:
        """
        Extracts scale, offset, and nodata for a given band from the first STAC item.
        Assumes these properties are consistent across items for the same band.
        Caches results to avoid redundant extraction.
        """
        if band_name in self._band_properties_cache:
            return self._band_properties_cache[band_name]

        if not self.items:
            self._search_items()
        
        if not self.items:
            print(f"Warning: No STAC items found to extract properties for band '{band_name}'.")
            return {'scale': 1.0, 'offset': 0.0, 'nodata': None}

        # Use the first item to get band properties
        # Asset keys in STAC items should match the 'bands_to_load' names
        first_item = self.items[0]
        scale = 1.0
        offset = 0.0
        nodata = None

        if band_name in first_item.assets:
            asset = first_item.assets[band_name]
            raster_bands_info = asset.extra_fields.get('raster:bands', [{}])
            if raster_bands_info and isinstance(raster_bands_info, list) and len(raster_bands_info) > 0:
                band_meta = raster_bands_info[0]
                scale = band_meta.get('scale', 1.0)
                offset = band_meta.get('offset', 0.0)
                nodata = band_meta.get('nodata') # Can be 0 or other value
            else:
                print(f"Warning: 'raster:bands' metadata missing or malformed for asset '{band_name}' in item '{first_item.id}'.")
        else:
            print(f"Warning: Asset '{band_name}' not found in first STAC item '{first_item.id}'.")

        properties = {'scale': scale, 'offset': offset, 'nodata': nodata}
        self._band_properties_cache[band_name] = properties
        return properties

    def compute_ndvi(self, resolution=10):
        """
        Loads 'red' and 'nir' bands and computes NDVI.
        Assumes that odc.stac.load handles scale/offset factors from STAC metadata.

        Args:
            resolution (int): Spatial resolution for loading bands.

        Returns:
            xarray.DataArray: Calculated NDVI, or None if bands could not be loaded.
        """
        bands_dataset = self.load_bands(bands_to_load=('red', 'nir'), resolution=resolution)

        if bands_dataset is None or not bands_dataset.data_vars:
            print("Could not load 'red' and 'nir' bands for NDVI calculation.")
            return None
        
        if "nir" not in bands_dataset:
            print("Error: 'nir' band not found in loaded dataset.")
            return None
        if "red" not in bands_dataset:
            print("Error: 'red' band not found in loaded dataset.")
            return None

        nir_band = bands_dataset["nir"]
        red_band = bands_dataset["red"]

        # Add a small epsilon to the denominator to prevent division by zero errors
        epsilon = 1e-8 
        ndvi = (nir_band - red_band) / (nir_band + red_band + epsilon)
        ndvi.name = "ndvi"
        
        return ndvi

def get_ndvi(region, start_date: str, end_date: str, cloud_cover: float):
    """
    High-level function to get NDVI for a given region and parameters.
    This instantiates Sentinel2Connector and calls its compute_ndvi method.
    """
    connector = Sentinel2Connector(region, start_date, end_date, cloud_cover)
    ndvi_array = connector.compute_ndvi(resolution=10)
    
    if ndvi_array is None:
        print("Failed to compute NDVI.")
        # Optionally, could return an empty DataArray or raise an error
        
    return ndvi_array