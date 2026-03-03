"""权限管理 CRUD 数据库操作层"""
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from backend.models.permission import Permission
from backend.schemas.permission_schema import PermissionCreate, PermissionUpdate


def _permission_query(db: Session):
    """带预加载的基础查询，避免序列化时 lazy-load 报错"""
    return db.query(Permission).options(
        selectinload(Permission.roles),
        selectinload(Permission.children),
    )


def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
    """获取权限列表"""
    return _permission_query(db).offset(skip).limit(limit).all()


def get_permission_by_id(db: Session, permission_id: int) -> Optional[Permission]:
    """根据ID获取权限"""
    return _permission_query(db).filter(Permission.id == permission_id).first()


def get_permission_by_code(db: Session, code: str) -> Optional[Permission]:
    """根据权限编码获取权限"""
    return db.query(Permission).filter(Permission.code == code).first()


def get_permissions_by_parent_id(db: Session, parent_id: int) -> List[Permission]:
    """根据父级ID获取子权限列表"""
    return db.query(Permission).filter(Permission.parent_id == parent_id).all()


def get_top_level_permissions(db: Session) -> List[Permission]:
    """获取顶级权限列表（parent_id 为空）"""
    return _permission_query(db).filter(Permission.parent_id.is_(None)).all()


def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    """创建新权限"""
    db_permission = Permission(
        name=permission.name,
        code=permission.code,
        type=permission.type,
        path=permission.path,
        method=permission.method,
        description=permission.description,
        parent_id=permission.parent_id,
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def update_permission(db: Session, permission_id: int, permission_update: PermissionUpdate) -> Optional[Permission]:
    """更新权限"""
    db_permission = get_permission_by_id(db, permission_id)
    if not db_permission:
        return None

    update_data = permission_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_permission, key, value)

    db.commit()
    db.refresh(db_permission)
    return db_permission


def delete_permission(db: Session, permission_id: int) -> bool:
    """删除权限"""
    db_permission = get_permission_by_id(db, permission_id)
    if not db_permission:
        return False

    db.delete(db_permission)
    db.commit()
    return True
