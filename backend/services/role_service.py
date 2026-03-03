"""角色管理业务逻辑层"""
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.models.role import Role
from backend.models.permission import Permission
from backend.schemas.role_schema import RoleCreate, RoleUpdate
from backend.crud import crud_role


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """获取角色列表"""
    return crud_role.get_roles(db, skip=skip, limit=limit)


def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
    """根据ID获取角色"""
    return crud_role.get_role_by_id(db, role_id)


def get_role_by_code(db: Session, role_code: str) -> Optional[Role]:
    """根据角色编码获取角色"""
    return crud_role.get_role_by_code(db, role_code)


def create_role(db: Session, role: RoleCreate) -> Role:
    """创建新角色"""
    return crud_role.create_role(db, role)


def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
    """更新角色"""
    return crud_role.update_role(db, role_id, role_update)


def delete_role(db: Session, role_id: int) -> bool:
    """删除角色"""
    return crud_role.delete_role(db, role_id)


# ---- 角色权限管理 ----

def get_role_permissions(db: Session, role_id: int) -> List[Permission]:
    """获取角色已分配的权限列表"""
    return crud_role.get_role_permissions(db, role_id)


def assign_permissions_to_role(db: Session, role_id: int, permission_ids: List[int]) -> bool:
    """为角色批量分配权限"""
    return crud_role.assign_permissions_to_role(db, role_id, permission_ids)


def remove_permissions_from_role(db: Session, role_id: int, permission_ids: List[int]) -> bool:
    """从角色批量移除权限"""
    return crud_role.remove_permissions_from_role(db, role_id, permission_ids)

