from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class SourceResponse(SourceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class WeightConfig(BaseModel):
    operator_id: int
    weight: int


class WeightConfigRequest(BaseModel):
    weights: List[WeightConfig]
