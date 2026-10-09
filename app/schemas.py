from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    feature_count: int
    crs: Optional[str] = None
    projected_crs: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeasurementResponse(BaseModel):
    feature_id: int
    feature_index: int
    geometry_type: str

    area: Optional[float] = None
    perimeter: Optional[float] = None
    length: Optional[float] = None

    unit: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class MeasurementsResponse(BaseModel):
    file_id: str
    filename: str
    measurements: list[MeasurementResponse]