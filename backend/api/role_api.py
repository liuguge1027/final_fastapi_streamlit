"""角色管理 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.schemas.role_schema import RoleInfo, RoleCreate, RoleUpdate
from backend.services import role_service
from backend.core.auth import get_current_user

router = APIRouter(
    prefix="/roles",
    tags=["角色管理"],
    dependencies=[Depends(get_current_user)]  # 所有接口均需登录
)


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
