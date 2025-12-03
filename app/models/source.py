from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    # Relationships
    weights = relationship(
        "OperatorWeight", back_populates="source", cascade="all, delete-orphan"
    )
    appeals = relationship("Appeal", back_populates="source")
