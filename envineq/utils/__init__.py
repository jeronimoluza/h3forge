from shapely import wkt, Polygon, MultiPolygon


def load_wkt(wkt: str) -> Polygon | MultiPolygon:
    return wkt.loads(wkt)
