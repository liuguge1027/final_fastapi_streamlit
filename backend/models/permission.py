from sqlalchemy import (
    Column, BigInteger, String, Text, DateTime, func, ForeignKey,
)
from sqlalchemy.orm import relationship
from backend.db.database import Base


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    name = Column(String(100), nullable=False, comment="权限名称")
    code = Column(String(100), unique=True, nullable=False, comment="唯一权限编码，如 user:create")
    type = Column(String(20), nullable=False, comment="权限类型（menu/api/button）")
    path = Column(String(255), nullable=True, comment="对应 API 路径")
    method = Column(String(20), nullable=True, comment="对应 HTTP 方法")
    description = Column(Text, nullable=True, comment="权限描述")
    parent_id = Column(BigInteger, ForeignKey("permissions.id"), nullable=True, comment="父级权限ID，自关联")
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

    # 多对多：权限 ↔ 角色
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    # 自关联：子权限
    children = relationship("Permission", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<Permission(id={self.id}, code='{self.code}')>"
