"""权限相关 Pydantic Schema"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


# ---- 辅助 Schema ----

class RoleBrief(BaseModel):
    """角色简要信息（仅 id + role_name，用于权限返回）"""
    id: int
    role_name: str

    model_config = ConfigDict(from_attributes=True)


# ---- Permission Schema ----

class PermissionCreate(BaseModel):
    """创建权限请求"""
    name: str
    code: str
    type: str
    path: Optional[str] = None
    method: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


class PermissionUpdate(BaseModel):
    """更新权限请求"""
    name: Optional[str] = None
    code: Optional[str] = None
    type: Optional[str] = None
    path: Optional[str] = None
    method: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


class PermissionRead(BaseModel):
    """权限详细信息（含子权限递归 + 关联角色简要）"""
    id: int
    name: str
    code: str
    type: str
    path: Optional[str] = None
    method: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    children: List["PermissionRead"] = []
    roles: List[RoleBrief] = []

    model_config = ConfigDict(from_attributes=True)


# 递归模型需要显式 rebuild
PermissionRead.model_rebuild()

# 别名：与 RoleInfo 命名风格一致，API 层使用 PermissionInfo
PermissionInfo = PermissionRead


# ---- RolePermission Schema ----

class RolePermissionRead(BaseModel):
    """角色-权限中间表"""
    id: int
    role_id: int
    permission_id: int

    model_config = ConfigDict(from_attributes=True)
