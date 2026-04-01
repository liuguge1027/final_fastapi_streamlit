"""全局认证依赖：从 Authorization Header 读取 Bearer Token 并验证"""
import jwt
from fastapi import Request, HTTPException, status

from backend.core.security import SECRET_KEY, ALGORITHM
from backend.db.database import SessionLocal
from backend.services.user_service import get_user_by_username


def get_current_user(request: Request):
    """
    FastAPI Depends 依赖函数。
    从请求的 Authorization Header 中提取 Bearer Token，校验 JWT，
    并返回对应的数据库用户对象。
    """
    # 1. 优先使用 JWT（即使来自白名单 IP），确保权限校验基于真实用户
    #    IP 白名单仅在「无 Token」时兜底放行（如直接用 curl 测试 API）
    client_ip = request.client.host if request.client else ""
    auth_header = request.headers.get("Authorization", "")
    has_token = auth_header.startswith("Bearer ")

    if not has_token and client_ip in ["127.0.0.1", "192.168.1.2"]:
        db = SessionLocal()
        try:
            from backend.models.user import User
            user = db.query(User).order_by(User.is_superuser.desc()).first()
            if user:
                return user
        finally:
            db.close()

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌，请先登录",
        )

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 载荷无效",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 已过期，请重新登录",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效",
        )

    db = SessionLocal()
    try:
        user = get_user_by_username(db, username=username)
    finally:
        db.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return user


def require_permission(permission_code: str):
    """
    权限校验依赖工厂。
    返回一个 FastAPI Depends 函数，检查当前用户的角色是否拥有指定权限编码。

    用法:
        @router.post("", dependencies=[Depends(require_permission("role:create"))])
        def create_role(...):
            ...

    规则:
        - is_superuser=1 的用户直接放行（超级管理员拥有所有权限）
        - 其他用户必须通过 role → role_permissions → permissions 链路拥有该 code
        - 未授权则返回 403 Forbidden
    """
    def _check(request: Request):
        from backend.models.user import User
        from backend.models.role import Role
        from sqlalchemy.orm import selectinload

        user = get_current_user(request)

        # 超级管理员直接放行
        if user.is_superuser:
            return user

        db = SessionLocal()
        try:
            db_user = (
                db.query(User)
                .options(
                    selectinload(User.role).selectinload(Role.permissions)
                )
                .filter(User.id == user.id)
                .first()
            )

            if not db_user or not db_user.role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无操作权限（{permission_code}）：用户未分配角色",
                )

            user_permission_codes = {p.code for p in db_user.role.permissions}
        finally:
            db.close()

        if permission_code not in user_permission_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无操作权限：需要 [{permission_code}]，请联系管理员",
            )

        return user

    return _check
