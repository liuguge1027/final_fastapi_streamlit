"""认证服务层"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from backend.core.security import verify_password
from backend.models.user import User


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    认证用户：查询数据库 → 检查账号状态 → 验证密码 → 更新登录信息。
    成功返回 User 对象，失败返回 None。
    """
    user = db.query(User).options(joinedload(User.role)).filter(User.username == username).first()
    if not user:
        return None

    # 检查账号是否被禁用
    if not user.is_active:
        return None

    # 检查账号是否被锁定
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        return None

    # 验证密码
    if not verify_password(password, user.password_hash):
        # 登录失败，累加失败次数
        user.failed_login_count = (user.failed_login_count or 0) + 1
        db.commit()
        return None

    # 登录成功：重置失败次数，更新最后登录时间
    user.failed_login_count = 0
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    return user
