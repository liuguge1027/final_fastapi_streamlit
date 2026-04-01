from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RoleMenuBase(BaseModel):
    role_code: str
    main_menu: str
    sub_menu: str
    module_path: Optional[str] = None
    sort_order: int = 0

class RoleMenuCreate(RoleMenuBase):
    pass

class RoleMenuUpdate(BaseModel):
    role_code: Optional[str] = None
    main_menu: Optional[str] = None
    sub_menu: Optional[str] = None
    module_path: Optional[str] = None
    sort_order: Optional[int] = None

class RoleMenu(RoleMenuBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
