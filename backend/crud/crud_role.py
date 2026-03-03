"""角色管理 CRUD 数据库操作层"""
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from backend.models.role import Role
from backend.models.permission import Permission
from backend.models.role_permission import RolePermission
from backend.schemas.role_schema import RoleCreate, RoleUpdate


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """获取角色列表"""
    return db.query(Role).offset(skip).limit(limit).all()


def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
    """根据ID获取角色"""
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_code(db: Session, role_code: str) -> Optional[Role]:
    """根据角色编码获取角色"""
    return db.query(Role).filter(Role.role_code == role_code).first()


def create_role(db: Session, role: RoleCreate) -> Role:
    """创建新角色"""
    db_role = Role(
        role_name=role.role_name,
        role_code=role.role_code,
        description=role.description,
        status=role.status or 1,
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
    """更新角色"""
    db_role = get_role_by_id(db, role_id)
    if not db_role:
        return None

    update_data = role_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_role, key, value)

    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int) -> bool:
    """删除角色"""
    db_role = get_role_by_id(db, role_id)
    if not db_role:
        return False

    db.delete(db_role)
    db.commit()
    return True


# ---- 角色权限管理 ----

def get_role_permissions(db: Session, role_id: int) -> List[Permission]:
    """获取角色已分配的权限列表"""
    role = (
        db.query(Role)
        .options(selectinload(Role.permissions))
        .filter(Role.id == role_id)
        .first()
    )
    if not role:
        return []
    return role.permissions


def assign_permissions_to_role(db: Session, role_id: int, permission_ids: List[int]) -> bool:
    """为角色批量分配权限"""
    role = get_role_by_id(db, role_id)
    if not role:
        return False

    for pid in permission_ids:
        existing = (
            db.query(RolePermission)
            .filter(RolePermission.role_id == role_id, RolePermission.permission_id == pid)
            .first()
        )
        if not existing:
            db.add(RolePermission(role_id=role_id, permission_id=pid))

    db.commit()
    return True


def remove_permissions_from_role(db: Session, role_id: int, permission_ids: List[int]) -> bool:
    """从角色批量移除权限"""
    role = get_role_by_id(db, role_id)
    if not role:
        return False

    db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id.in_(permission_ids),
    ).delete(synchronize_session=False)

    db.commit()
    return True

