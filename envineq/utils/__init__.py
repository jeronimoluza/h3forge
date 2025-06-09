from shapely import wkt, Polygon, MultiPolygon


def load_wkt(wkt_str: str) -> Polygon | MultiPolygon:
    return wkt.loads(wkt_str)
