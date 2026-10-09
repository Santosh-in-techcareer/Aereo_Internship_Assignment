from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)

    feature_count = Column(Integer, default=1)

    crs = Column(String, nullable=True)
    projected_crs = Column(String, nullable=True)

    status = Column(String, default="PROCESSING")

    error_message = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    features = relationship(
        "Feature",
        back_populates="file",
        cascade="all, delete-orphan",
    )


class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True)

    file_id = Column(
        String,
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
    )

    feature_index = Column(Integer, nullable=False)

    geometry_type = Column(String, nullable=False)

    geometry_wkt = Column(Text, nullable=True)

    crs = Column(String, nullable=True)

    properties = Column(JSON, nullable=True)

    area = Column(Float, nullable=True)

    perimeter = Column(Float, nullable=True)

    length = Column(Float, nullable=True)

    measurement_unit = Column(String, nullable=True)

    measurement_status = Column(String, nullable=True)

    file = relationship(
        "File",
        back_populates="features",
    )