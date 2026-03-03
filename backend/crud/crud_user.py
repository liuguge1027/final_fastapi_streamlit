"""用户管理 CRUD 数据库操作层"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from backend.models.user import User


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """获取用户列表（预加载角色信息）"""
    return db.query(User).options(joinedload(User.role)).offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户（预加载角色信息）"""
    return db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user_data: dict) -> User:
    """创建新用户（接收已处理好的字典数据）"""
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, update_data: dict) -> Optional[User]:
    """更新用户（接收已处理好的字典数据）"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True
