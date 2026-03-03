"""角色相关 Pydantic Schema"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RoleBase(BaseModel):
    """角色基础信息"""
    role_name: str
    role_code: str
    description: Optional[str] = None
    status: Optional[int] = 1


class RoleCreate(RoleBase):
    """创建角色请求"""
    pass


class RoleUpdate(BaseModel):
    """更新角色请求"""
    role_name: Optional[str] = None
    role_code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None


class RoleInfo(RoleBase):
    """角色详细信息"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
