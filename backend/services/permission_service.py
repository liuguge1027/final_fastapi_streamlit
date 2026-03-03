"""权限管理业务逻辑层"""
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.models.permission import Permission
from backend.schemas.permission_schema import PermissionCreate, PermissionUpdate
from backend.crud import crud_permission


def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
    """获取权限列表"""
    return crud_permission.get_permissions(db, skip=skip, limit=limit)


def get_permission_by_id(db: Session, permission_id: int) -> Optional[Permission]:
    """根据ID获取权限"""
    return crud_permission.get_permission_by_id(db, permission_id)


def get_permission_by_code(db: Session, code: str) -> Optional[Permission]:
    """根据权限编码获取权限"""
    return crud_permission.get_permission_by_code(db, code)


def get_permission_tree(db: Session) -> List[Permission]:
    """获取权限树（仅顶级节点，子节点通过 children relationship 自动加载）"""
    return crud_permission.get_top_level_permissions(db)


def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    """创建新权限"""
    return crud_permission.create_permission(db, permission)


def update_permission(db: Session, permission_id: int, permission_update: PermissionUpdate) -> Optional[Permission]:
    """更新权限"""
    return crud_permission.update_permission(db, permission_id, permission_update)


def delete_permission(db: Session, permission_id: int) -> bool:
    """删除权限"""
    return crud_permission.delete_permission(db, permission_id)
