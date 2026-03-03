"""认证路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.schemas.user_schema import LoginRequest, LoginResponse
from backend.services.auth_service import authenticate_user
from backend.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录接口"""
    user = authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 获取角色编码
    role_code = user.role.role_code if user.role else "USER"

    # 生成 JWT token
    token = create_access_token(data={
        "sub": user.username,
        "role": role_code,
        "is_superuser": bool(user.is_superuser),
    })

    return LoginResponse(
        access_token=token,
        username=user.username,
        role=role_code,
        is_superuser=bool(user.is_superuser),
    )
