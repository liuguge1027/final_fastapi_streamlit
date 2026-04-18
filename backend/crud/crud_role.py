"""角色管理 CRUD 数据库操作层"""
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.models.role import Role
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
