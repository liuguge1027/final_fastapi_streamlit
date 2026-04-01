from sqlalchemy import Column, BigInteger, String, DateTime, Integer, func
from backend.db.database import Base

class RoleMenu(Base):
    """角色菜单表"""
    __tablename__ = "role_menus"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    role_code = Column(String(50), nullable=False, index=True, comment="角色编码，与前端约定如 admin, finance")
    main_menu = Column(String(100), nullable=False, comment="主菜单名称，如 系统管理")
    sub_menu = Column(String(100), nullable=False, comment="子菜单名称，如 用户管理")
    module_path = Column(String(200), nullable=True, comment="前端页面模块路径，如 views.admin.pages.user_page")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序权重")
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    def __repr__(self):
        return f"<RoleMenu(id={self.id}, role_code='{self.role_code}', main_menu='{self.main_menu}', sub_menu='{self.sub_menu}')>"
