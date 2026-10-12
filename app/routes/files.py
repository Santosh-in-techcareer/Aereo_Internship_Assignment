import shutil
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File as FastAPIFile,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

import pyproj
import shapely.geometry
import shapely.ops
import shapely.wkt

from ..database import SessionLocal, get_db
from ..models import File, Feature
from ..schemas import FileResponse
from ..services.file_process import process_geospatial_file


def to_geojson(geometry_wkt: str | None, crs_str: str | None):
    if not geometry_wkt:
        return None
    try:
        geom = shapely.wkt.loads(geometry_wkt)
        if crs_str and "4326" not in crs_str:
            transformer = pyproj.Transformer.from_crs(crs_str, "EPSG:4326", always_xy=True)
            geom = shapely.ops.transform(transformer.transform, geom)
        return shapely.geometry.mapping(geom)
    except Exception:
        return None


router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def process_in_background(
    file_path: Path,
    filename: str,
    file_id: str,
):
    db = SessionLocal()

    try:
        file_record = (
            db.query(File)
            .filter(File.id == file_id)
            .first()
        )

        if not file_record:
            return

        process_geospatial_file(
            file_path=file_path,
            original_filename=filename,
            db=db,
            file_record=file_record,
        )

    except Exception as exc:
        print(f"Background processing failed: {exc}")

        db.rollback()

        file_record = (
            db.query(File)
            .filter(File.id == file_id)
            .first()
        )

        if file_record:
            file_record.status = "FAILED"
            file_record.error_message = str(exc)
            db.commit()

    finally:
        db.close()

        if file_path.exists():
            file_path.unlink()


@router.post(
    "/",
    response_model=FileResponse,
)
async def upload_file(
    background_tasks: BackgroundTasks,
    uploaded_file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
):
    filename = uploaded_file.filename or ""

    extension = Path(filename).suffix.lower()

    if extension not in {".kml", ".zip"}:
        raise HTTPException(
            status_code=400,
            detail="Only .kml and .zip files are supported.",
        )

    if uploaded_file.size and uploaded_file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the 50 MB limit.",
        )

    file_id = str(uuid.uuid4())

    destination = UPLOAD_DIR / f"{file_id}{extension}"

    total_size = 0
    with destination.open("wb") as buffer:
        while chunk := await uploaded_file.read(1024 * 1024):
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                buffer.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=400,
                    detail="File size exceeds the 50 MB limit.",
                )
            buffer.write(chunk)

    file_type = (
        "KML"
        if extension == ".kml"
        else "SHAPEFILE_ZIP"
    )

    file_record = File(
        id=file_id,
        filename=filename,
        file_type=file_type,
        status="PROCESSING",
    )

    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    background_tasks.add_task(
        process_in_background,
        destination,
        filename,
        file_id,
    )

    return file_record


@router.get(
    "/{file_id}/",
    response_model=FileResponse,
)
def get_file(
    file_id: str,
    db: Session = Depends(get_db),
):
    file_record = (
        db.query(File)
        .filter(File.id == file_id)
        .first()
    )

    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    return file_record
@router.get(
    "/{file_id}/measurements/"
)
def get_measurements(
    file_id: str,
    db: Session = Depends(get_db),
):
    file_record = (
        db.query(File)
        .filter(File.id == file_id)
        .first()
    )

    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    features = (
        db.query(Feature)
        .filter(Feature.file_id == file_id)
        .order_by(Feature.feature_index)
        .all()
    )

    return {
        "file_id": file_id,
        "filename": file_record.filename,
        "measurements": [
            {
                "feature_id": feature.id,
                "feature_index": feature.feature_index,
                "geometry_type": feature.geometry_type,
                "area": feature.area,
                "perimeter": feature.perimeter,
                "length": feature.length,
                "unit": feature.measurement_unit,
                "status": feature.measurement_status,
                "geojson": to_geojson(feature.geometry_wkt, feature.crs),
            }
            for feature in features
        ],
    }