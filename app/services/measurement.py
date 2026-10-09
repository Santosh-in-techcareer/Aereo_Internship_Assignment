from shapely.geometry.base import BaseGeometry


def calculate_measurement(geometry):
    geometry_type = geometry.geom_type

    if geometry_type in ["Polygon", "MultiPolygon"]:
        return {
            "area": round(geometry.area, 2),
            "perimeter": round(geometry.length, 2),
            "length": None,
            "unit": "m² / m",
            "status": "SUPPORTED"
        }

    elif geometry_type in ["LineString", "MultiLineString"]:
        return {
            "area": None,
            "perimeter": None,
            "length": round(geometry.length, 2),
            "unit": "m",
            "status": "SUPPORTED"
        }

    elif geometry_type in ["Point", "MultiPoint"]:
        return {
            "area": None,
            "perimeter": None,
            "length": None,
            "unit": None,
            "status": "NO_MEASUREMENT"
        }

    else:
        return {
            "area": None,
            "perimeter": None,
            "length": None,
            "unit": None,
            "status": "UNSUPPORTED"
        }