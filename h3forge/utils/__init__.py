from shapely import wkt, Polygon, MultiPolygon


def load_wkt(wkt_str: str) -> Polygon | MultiPolygon:
    """
    Loads a WKT string into a Shapely geometry object.
    
    Args:
        wkt_str (str): The WKT string to load.
    
    Returns:
        Polygon | MultiPolygon: The loaded Shapely geometry object.
    """
    return wkt.loads(wkt_str)
