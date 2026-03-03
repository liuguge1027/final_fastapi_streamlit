"""用户管理业务逻辑层"""
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.models.user import User
from backend.core.security import hash_password
from backend.schemas.user_schema import UserCreate, UserUpdate
from backend.crud import crud_user


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """获取用户列表"""
    return crud_user.get_users(db, skip=skip, limit=limit)


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return crud_user.get_user_by_id(db, user_id)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return crud_user.get_user_by_username(db, username)


def create_user(db: Session, user: UserCreate) -> User:
    """创建新用户（业务层处理密码哈希）"""
    user_data = {
        "username": user.username,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "role_id": user.role_id,
        "is_active": user.is_active or 1,
        "is_superuser": user.is_superuser or 0,
    }
    return crud_user.create_user(db, user_data)


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """更新用户（业务层处理密码哈希）"""
    update_data = user_update.model_dump(exclude_unset=True)

    # 如果更新密码，需要哈希
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    return crud_user.update_user(db, user_id, update_data)


def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    return crud_user.delete_user(db, user_id)
