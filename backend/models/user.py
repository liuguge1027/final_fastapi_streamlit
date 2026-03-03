from sqlalchemy import (
    Column, BigInteger, String, DateTime, Integer, func, ForeignKey,
)
from sqlalchemy.orm import relationship
from backend.db.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    username = Column(String(50), unique=True, nullable=False, comment="登录用户名")
    email = Column(String(100), unique=True, nullable=True, comment="邮箱，可选登录")
    password_hash = Column(String(255), nullable=False, comment="哈希后的密码")
    salt = Column(String(50), nullable=True, comment="密码哈希盐（bcrypt/Argon2 可不用）")
    role_id = Column(BigInteger, ForeignKey("roles.id"), nullable=True, comment="关联角色ID")
    is_active = Column(Integer, nullable=False, default=1, comment="是否启用账号")
    is_superuser = Column(Integer, nullable=False, default=0, comment="是否超级管理员")
    last_login = Column(DateTime, nullable=True, comment="上次登录时间")
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间",
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    failed_login_count = Column(Integer, nullable=False, default=0, comment="连续失败登录次数")
    locked_until = Column(DateTime, nullable=True, comment="账号锁定截止时间")

    role = relationship("Role", back_populates="users")
    operation_logs = relationship("OperationLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
