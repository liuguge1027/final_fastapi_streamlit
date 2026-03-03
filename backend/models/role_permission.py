from sqlalchemy import (
    Column, BigInteger, ForeignKey,
)
from backend.db.database import Base


class RolePermission(Base):
    """角色-权限中间表"""
    __tablename__ = "role_permissions"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    role_id = Column(BigInteger, ForeignKey("roles.id"), nullable=False, comment="关联角色ID")
    permission_id = Column(BigInteger, ForeignKey("permissions.id"), nullable=False, comment="关联权限ID")

    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
