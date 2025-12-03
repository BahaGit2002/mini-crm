from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class OperatorWeight(Base):
    __tablename__ = "operator_weights"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    weight = Column(Integer, default=1)

    # Relationships
    operator = relationship("Operator", back_populates="weights")
    source = relationship("Source", back_populates="weights")
