from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    max_load = Column(Integer, default=10)

    # Relationships
    weights = relationship(
        "OperatorWeight", back_populates="operator",
        cascade="all, delete-orphan"
    )
    appeals = relationship("Appeal", back_populates="operator")
