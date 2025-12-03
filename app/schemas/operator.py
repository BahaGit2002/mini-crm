from pydantic import BaseModel, ConfigDict
from typing import Optional


class OperatorBase(BaseModel):
    name: str
    is_active: bool = True
    max_load: int = 10


class OperatorCreate(OperatorBase):
    pass


class OperatorUpdate(BaseModel):
    is_active: Optional[bool] = None
    max_load: Optional[int] = None


class OperatorResponse(OperatorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OperatorWithLoad(OperatorResponse):
    current_load: int
