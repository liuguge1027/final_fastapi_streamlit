#!/usr/bin/env python3
"""数据库初始化脚本
=================
第一次使用时运行，会：
1. 创建数据库（如果不存在）
2. 扫描并创建所有模型对应的表
3. 初始化 Alembic 迁移状态（stamp head）
4. 初始化角色数据
5. 初始化管理员账号

注意：
- 第一次使用运行此脚本
- 以后修改模型用：python migrate_db.py
"""
import sys
import os
import importlib
import pkgutil

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from backend.core.config import settings
from backend.core.security import hash_password
from backend.db.database import SessionLocal, Base, engine as db_engine

# 核心：必须导入所有模型以注册到 Base.metadata
def import_models():
    """动态导入 backend.models 下的所有模块"""
    import backend.models as models_pkg
    pkg_path = models_pkg.__path__
    for _, name, is_pkg in pkgutil.iter_modules(pkg_path):
        full_module_name = f"backend.models.{name}"
        importlib.import_module(full_module_name)
    print("✓ 所有模型已扫描并加载")

def create_database():
    """创建数据库（如果不存在）"""
    print("=== 步骤 1: 创建数据库 ===")
    
    # 先连接到MySQL服务器（不指定数据库）
    db_url_without_db = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}"
    temp_engine = create_engine(db_url_without_db)
    
    try:
        with temp_engine.connect() as conn:
            # 创建数据库
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
            print(f"✓ 数据库 '{settings.MYSQL_DB}' 创建完成\n")
    except Exception as e:
        print(f"✗ 创建数据库失败: {e}")
        sys.exit(1)

def create_tables():
    """根据模型创建所有数据表"""
    print("=== 步骤 2: 创建数据表 ===")
    import_models()
    try:
        # 显式使用 Base.metadata.create_all
        Base.metadata.create_all(bind=db_engine)
        print("✓ 所有模型表已创建完成\n")
    except Exception as e:
        print(f"✗ 创建表失败: {e}")
        sys.exit(1)

def stamp_alembic():
    """标记 Alembic 为最新版本，避免后续迁移冲突"""
    print("=== 步骤 3: 初始化迁移状态 (Alembic Stamp) ===")
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.stamp(alembic_cfg, "head")
        print("✓ Alembic 迁移状态已更新至最新 (head)\n")
    except Exception as e:
        print(f"⚠ Alembic Stamp 失败 (可选步骤): {e}")

def init_roles(db):
    """初始化基础角色数据"""
    print("=== 步骤 4: 初始化角色数据 ===")
    from backend.models.role import Role
    
    default_roles = [
        {"role_name": "管理员", "role_code": "ADMIN", "description": "系统最高权限管理员", "status": 1},
        {"role_name": "销售角色", "role_code": "SALE", "description": "负责销售报表查看与客户管理", "status": 1},
        {"role_name": "人力资源", "role_code": "HR", "description": "负责员工管理与绩效考核", "status": 1},
        {"role_name": "财务角色", "role_code": "FINANCE", "description": "负责财务收入与支出报表", "status": 1},
    ]
    
    for role_data in default_roles:
        existing_role = db.query(Role).filter(Role.role_code == role_data["role_code"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            print(f"✓ 添加角色: {role_data['role_code']}")
        else:
            print(f"· 角色已存在: {role_data['role_code']}")
    
    db.commit()

def init_admin_user(db):
    """初始化超管账号"""
    print("\n=== 步骤 5: 初始化管理员账号 ===")
    from backend.models.user import User
    from backend.models.role import Role
    
    # 获取 ADMIN 角色
    admin_role = db.query(Role).filter(Role.role_code == "ADMIN").first()
    if not admin_role:
        print("✗ 错误: ADMIN 角色未找到，跳过管理员创建")
        return
    
    # 检查是否已存在 superuser
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("· 管理员账号已存在: admin")
        return
    
    # 创建默认管理员 (请提醒用户修改默认密码)
    admin_password = "admin123"
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password(admin_password),
        role_id=admin_role.id,
        is_active=1,
        is_superuser=1
    )
    
    db.add(admin_user)
    db.commit()
    print("✓ 管理员账号初始化完成")
    print(f"  用户名: admin")
    print(f"  初始密码: {admin_password} (登录后请务必修改)")

def main():
    print("=" * 60)
    print("🚀 开始初始化数据库环境")
    print("=" * 60 + "\n")
    
    # 1. 确保数据库存在
    create_database()
    
    # 2. 创建所有表
    create_tables()
    
    # 3. 关联 Alembic
    stamp_alembic()
    
    # 4. 填充初始数据
    print("=== 步骤 4/5: 填充初始数据 ===")
    db = SessionLocal()
    try:
        init_roles(db)
        init_admin_user(db)
        print("\n" + "✓ 初始数据填充完成")
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("✨ 数据库初始化成功！")
    print("=" * 60)
    print("\n提示：后续若需修改数据模型，请运行 `python migrate_db.py` 更新数据库。")

if __name__ == "__main__":
    main()

