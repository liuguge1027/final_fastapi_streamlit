"""角色管理 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.schemas.role_schema import RoleInfo, RoleCreate, RoleUpdate
from backend.api.permission_api import _permission_to_dict
from backend.services import role_service

router = APIRouter(prefix="/roles", tags=["角色管理"])


# ---- 请求体 Schema ----

class PermissionIdsRequest(BaseModel):
    """权限 ID 列表请求体"""
    permission_ids: List[int]


# ---- 角色 CRUD ----

@router.get("", response_model=List[RoleInfo])
def get_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取角色列表"""
    return role_service.get_roles(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleInfo)
def get_role(role_id: int, db: Session = Depends(get_db)):
    """获取单个角色"""
    role = role_service.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return role


@router.post("", response_model=RoleInfo)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """创建新角色"""
    existing_role = role_service.get_role_by_code(db, role.role_code)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色编码已存在"
        )
    return role_service.create_role(db, role)


@router.put("/{role_id}", response_model=RoleInfo)
def update_role(role_id: int, role_update: RoleUpdate, db: Session = Depends(get_db)):
    """更新角色"""
    role = role_service.update_role(db, role_id, role_update)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return role


@router.delete("/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """删除角色"""
    success = role_service.delete_role(db, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return {"message": "删除成功"}


# ---- 角色权限管理 ----

@router.get("/{role_id}/permissions")
def get_role_permissions(role_id: int, db: Session = Depends(get_db)):
    """获取角色已分配的权限列表"""
    perms = role_service.get_role_permissions(db, role_id)
    return [_permission_to_dict(p) for p in perms]


@router.post("/{role_id}/permissions")
def assign_permissions(role_id: int, body: PermissionIdsRequest, db: Session = Depends(get_db)):
    """为角色批量分配权限"""
    success = role_service.assign_permissions_to_role(db, role_id, body.permission_ids)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return {"message": "权限分配成功"}


@router.post("/{role_id}/permissions/remove")
def remove_permissions(role_id: int, body: PermissionIdsRequest, db: Session = Depends(get_db)):
    """从角色批量移除权限"""
    success = role_service.remove_permissions_from_role(db, role_id, body.permission_ids)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return {"message": "权限移除成功"}

