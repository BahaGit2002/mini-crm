from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)

    # Relationships
    appeals = relationship("Appeal", back_populates="lead")
