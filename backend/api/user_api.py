"""用户管理 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.schemas.user_schema import UserInfo, UserCreate, UserUpdate, UserDetail
from backend.services import user_service

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("", response_model=List[UserDetail])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取用户列表"""
    users = user_service.get_users(db, skip=skip, limit=limit)
    result = []
    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role_id": user.role_id,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "role_name": user.role.role_name if user.role else None,
            "role_code": user.role.role_code if user.role else None,
        }
        result.append(user_dict)
    return result


@router.get("/{user_id}", response_model=UserDetail)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取单个用户"""
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role_id": user.role_id,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "last_login": user.last_login,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "role_name": user.role.role_name if user.role else None,
        "role_code": user.role.role_code if user.role else None,
    }


@router.post("", response_model=UserInfo)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    existing_user = user_service.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    return user_service.create_user(db, user)


@router.put("/{user_id}", response_model=UserInfo)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """更新用户"""
    user = user_service.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return {"message": "删除成功"}
