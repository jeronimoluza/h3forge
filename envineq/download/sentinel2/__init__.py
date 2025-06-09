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
        
        # Ensure all bands are float and compute
        for band_name in data_stack.data_vars:
            if band_name in bands_to_load:
                data_stack[band_name] = data_stack[band_name].astype(float, copy=False).compute()

        return data_stack

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

        ndvi = (nir_band - red_band) / (nir_band + red_band)
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