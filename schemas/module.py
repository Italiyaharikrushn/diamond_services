from pydantic import BaseModel
from typing import Optional


class ModuleBase(BaseModel):
    code: str
    display_name: str
    parent_id : Optional[int] = None
    sequence: float
    is_header: bool = False


class ModuleCreate(ModuleBase):
    ...

class ModuleUpdate(ModuleBase):
    id: int


class ModuleInDBBase(ModuleBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

class Module(ModuleInDBBase):
    pass
