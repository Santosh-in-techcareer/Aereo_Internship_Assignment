import json
import math
import shutil
import tempfile
import zipfile
from pathlib import Path

import geopandas as gpd

from ..models import Feature, File
from .crs import get_projected_geodataframe
from .measurement import calculate_measurement


def get_file_type(filename: str) -> str:
    extension = Path(filename).suffix.lower()

    if extension == ".kml":
        return "KML"

    if extension == ".zip":
        return "SHAPEFILE_ZIP"

    raise ValueError(
        "Unsupported file type. Only .kml and .zip are allowed."
    )


def extract_shapefile(zip_path: Path, extract_dir: Path) -> Path:

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    shapefiles = list(extract_dir.rglob("*.shp"))

    if not shapefiles:
        raise ValueError(
            "ZIP file does not contain a Shapefile (.shp)."
        )

    if len(shapefiles) > 1:
        raise ValueError(
            "ZIP file contains multiple Shapefiles. "
            "Please upload a ZIP containing one Shapefile."
        )

    return shapefiles[0]


def make_json_serializable(value):

    if value is None:
        return None

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value

    if isinstance(value, dict):
        return {
            key: make_json_serializable(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            make_json_serializable(item)
            for item in value
        ]

    try:
        json.dumps(value)
        return value

    except (TypeError, ValueError):
        return str(value)


def process_geospatial_file(
    file_path: Path,
    original_filename: str,
    db,
    file_record: File,
):

    file_type = get_file_type(original_filename)

    working_directory = Path(
        tempfile.mkdtemp(prefix="geo_processing_")
    )

    try:

 
        # Determine actual file

        if file_type == "KML":
            actual_file = file_path

        else:
            actual_file = extract_shapefile(
                file_path,
                working_directory,
            )


        # Read geospatial data


        gdf = gpd.read_file(
            actual_file,
            engine="pyogrio",
        )

        if gdf.empty:
            raise ValueError(
                "The uploaded file contains no features."
            )

        if gdf.crs is None:
            raise ValueError(
                "The uploaded file does not contain CRS information."
            )

        source_crs = gdf.crs.to_string()

        file_record.crs = source_crs

 
        # Convert to projected CRS
 

        projected_gdf, projected_crs = (
            get_projected_geodataframe(gdf)
        )

        file_record.projected_crs = projected_crs

 
        # Process every feature
 

        for index, row in gdf.iterrows():

            geometry = row.geometry

            # Invalid / empty geometry
            if geometry is None or geometry.is_empty:

                feature = Feature(
                    file_id=file_record.id,
                    feature_index=int(index+1),
                    geometry_type="UNKNOWN",
                    geometry_wkt=None,
                    crs=source_crs,
                    properties={},
                    measurement_status="INVALID_GEOMETRY",
                )

                db.add(feature)

                continue

            # Projected geometry is used ONLY for measurement
            projected_geometry = (
                projected_gdf.loc[index].geometry
            )

            measurement = calculate_measurement(
                projected_geometry
            )

     
            # Extract properties
     

            properties = {}

            for key, value in row.items():

                if key == gdf.geometry.name:
                    continue

                properties[key] = make_json_serializable(value)

     
            # Save feature
     

            feature = Feature(
                file_id=file_record.id,
                feature_index=int(index+1),
                geometry_type=geometry.geom_type,
                geometry_wkt=geometry.wkt,
                crs=source_crs,
                properties=properties,
                area=measurement.get("area"),
                perimeter=measurement.get("perimeter"),
                length=measurement.get("length"),
                measurement_unit=measurement["unit"],
                measurement_status=measurement["status"],
            )

            db.add(feature)

 
        # Complete processing
 

        file_record.feature_count = len(gdf)
        file_record.status = "COMPLETED"
        file_record.error_message = None

        db.commit()

    except Exception as exc:

        db.rollback()

        file_record.status = "FAILED"
        file_record.error_message = str(exc)

        db.commit()

        raise

    finally:

        shutil.rmtree(
            working_directory,
            ignore_errors=True,
        )