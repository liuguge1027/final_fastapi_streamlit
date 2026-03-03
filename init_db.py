#!/usr/bin/env python3
"""数据库初始化脚本
=================
第一次使用时运行，会：
1. 创建数据库（如果不存在）
2. 使用 Alembic 迁移创建表
3. 初始化角色数据
4. 初始化管理员账号

注意：
- 第一次使用运行此脚本
- 以后修改模型用：python migrate_db.py
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.config import settings
from backend.core.security import hash_password
from backend.db.database import SessionLocal
from backend.models.user import User
from backend.models.role import Role
from sqlalchemy import create_engine, text


def create_database():
    """创建数据库（如果不存在）"""
    print("=== 创建数据库 ===")
    
    # 先连接到MySQL服务器（不指定数据库）
    db_url_without_db = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}"
    temp_engine = create_engine(db_url_without_db)
    
    with temp_engine.connect() as conn:
        # 创建数据库
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DB}"))
        conn.commit()
        print(f"✓ 数据库 '{settings.MYSQL_DB}' 创建完成\n")


def run_alembic_migrations():
    """使用 Alembic 迁移创建表"""
    print("=== 使用 Alembic 迁移创建表 ===")
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✓ Alembic 迁移完成\n")
    except ImportError:
        print("✗ Alembic 未安装")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Alembic 迁移失败: {e}")
        sys.exit(1)


def init_roles(db):
    """初始化角色数据"""
    print("=== 初始化角色数据 ===")
    
    default_roles = [
        {
            "role_name": "admin",
            "role_code": "ADMIN",
            "description": "管理员，拥有所有权限",
            "status": 1
        },
        {
            "role_name": "manager",
            "role_code": "MANAGER",
            "description": "经理，拥有部分管理权限",
            "status": 1
        },
        {
            "role_name": "user",
            "role_code": "USER",
            "description": "普通用户",
            "status": 1
        }
    ]
    
    for role_data in default_roles:
        existing_role = db.query(Role).filter(Role.role_code == role_data["role_code"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            print(f"✓ 添加角色: {role_data['role_code']}")
        else:
            print(f"- 角色已存在: {role_data['role_code']}")
    
    db.commit()
    print("✓ 角色数据初始化完成\n")


def init_admin_user(db):
    """初始化默认管理员账号"""
    print("=== 初始化管理员账号 ===")
    
    # 获取 ADMIN 角色
    admin_role = db.query(Role).filter(Role.role_code == "ADMIN").first()
    if not admin_role:
        print("✗ 错误: ADMIN 角色不存在，请先初始化角色数据")
        return
    
    # 检查管理员账号是否已存在
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("- 管理员账号已存在: admin")
        print("✓ 管理员账号初始化完成\n")
        return
    
    # 创建管理员账号
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        role_id=admin_role.id,
        is_active=1,
        is_superuser=1
    )
    
    db.add(admin_user)
    db.commit()
    print("✓ 创建管理员账号: admin")
    print("  用户名: admin")
    print("  密码: admin123")
    print("✓ 管理员账号初始化完成\n")


def main():
    print("=" * 60)
    print("数据库初始化脚本")
    print("=" * 60 + "\n")
    
    # 步骤 1: 创建数据库
    create_database()
    
    # 步骤 2: 使用 Alembic 迁移创建表
    run_alembic_migrations()
    
    # 步骤 3: 初始化数据
    db = SessionLocal()
    try:
        init_roles(db)
        init_admin_user(db)
    finally:
        db.close()
    
    print("=" * 60)
    print("✓ 数据库初始化完成!")
    print("=" * 60)
    print()
    print("以后修改模型请使用: python migrate_db.py")


if __name__ == "__main__":
    main()
