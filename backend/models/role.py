from sqlalchemy import (
    Column, BigInteger, String, Text, DateTime, Integer, func,
)
from sqlalchemy.orm import relationship
from backend.db.database import Base


class Role(Base):
    """角色表"""
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    role_name = Column(String(50), nullable=False, comment="角色名称，如 admin、user、finance")
    role_code = Column(String(50), unique=True, nullable=False, comment="唯一编码，用于程序判断，如 ADMIN、USER")
    description = Column(Text, nullable=True, comment="角色描述，便于管理")
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
    status = Column(Integer, nullable=False, default=1, comment="是否启用，方便禁用某个角色")

    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, role_name='{self.role_name}', role_code='{self.role_code}')>"
