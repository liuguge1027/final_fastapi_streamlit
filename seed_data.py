#!/usr/bin/env python3
"""
种子数据初始化脚本
================
插入权限、角色权限（赋予 ADMIN 角色）、操作日志的初始数据。

使用方式:
    cd /Users/lrq/Python项目/final_fastapi_streamlit
    python seed_data.py
"""
import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.db.database import SessionLocal
from backend.models.role import Role
from backend.models.user import User
from backend.models.permission import Permission
from backend.models.role_permission import RolePermission
from backend.models.operation_log import OperationLog


# =====================================================================
# 权限种子数据
# =====================================================================
PERMISSIONS = [
    # 用户管理权限
    {"name": "用户管理", "code": "user:manage", "type": "menu", "path": "/users", "method": None, "description": "用户管理菜单"},
    {"name": "用户列表", "code": "user:list", "type": "api", "path": "/users", "method": "GET", "description": "查看用户列表"},
    {"name": "创建用户", "code": "user:create", "type": "api", "path": "/users", "method": "POST", "description": "创建新用户"},
    {"name": "编辑用户", "code": "user:update", "type": "api", "path": "/users/{id}", "method": "PUT", "description": "编辑用户信息"},
    {"name": "删除用户", "code": "user:delete", "type": "api", "path": "/users/{id}", "method": "DELETE", "description": "删除用户"},
    # 角色管理权限
    {"name": "角色管理", "code": "role:manage", "type": "menu", "path": "/roles", "method": None, "description": "角色管理菜单"},
    {"name": "角色列表", "code": "role:list", "type": "api", "path": "/roles", "method": "GET", "description": "查看角色列表"},
    {"name": "创建角色", "code": "role:create", "type": "api", "path": "/roles", "method": "POST", "description": "创建新角色"},
    {"name": "编辑角色", "code": "role:update", "type": "api", "path": "/roles/{id}", "method": "PUT", "description": "编辑角色信息"},
    {"name": "删除角色", "code": "role:delete", "type": "api", "path": "/roles/{id}", "method": "DELETE", "description": "删除角色"},
    # 权限管理权限
    {"name": "权限管理", "code": "permission:manage", "type": "menu", "path": "/permissions", "method": None, "description": "权限管理菜单"},
    {"name": "权限列表", "code": "permission:list", "type": "api", "path": "/permissions", "method": "GET", "description": "查看权限列表"},
    {"name": "创建权限", "code": "permission:create", "type": "api", "path": "/permissions", "method": "POST", "description": "创建新权限"},
    {"name": "编辑权限", "code": "permission:update", "type": "api", "path": "/permissions/{id}", "method": "PUT", "description": "编辑权限"},
    {"name": "删除权限", "code": "permission:delete", "type": "api", "path": "/permissions/{id}", "method": "DELETE", "description": "删除权限"},
    # 角色权限管理权限
    {"name": "角色权限管理", "code": "role_permission:manage", "type": "menu", "path": "/role-permissions", "method": None, "description": "角色权限管理菜单"},
    {"name": "查看角色权限", "code": "role_permission:list", "type": "api", "path": "/roles/{id}/permissions", "method": "GET", "description": "获取角色的权限列表"},
    {"name": "分配角色权限", "code": "role_permission:create", "type": "api", "path": "/roles/{id}/permissions", "method": "POST", "description": "为角色分配权限"},
    {"name": "移除角色权限", "code": "role_permission:delete", "type": "api", "path": "/roles/{id}/permissions/remove", "method": "POST", "description": "从角色移除权限"},
    # 操作日志权限
    {"name": "日志管理", "code": "log:manage", "type": "menu", "path": "/operation-logs", "method": None, "description": "操作日志管理菜单"},
    {"name": "日志列表", "code": "log:list", "type": "api", "path": "/operation-logs", "method": "GET", "description": "查看操作日志"},
]


def seed_permissions(db):
    """插入权限种子数据"""
    print("=== 插入权限数据 ===")
    created_count = 0
    for perm_data in PERMISSIONS:
        existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if existing:
            print(f"  - 已存在: {perm_data['code']}")
            continue
        perm = Permission(
            name=perm_data["name"],
            code=perm_data["code"],
            type=perm_data["type"],
            path=perm_data.get("path"),
            method=perm_data.get("method"),
            description=perm_data.get("description"),
            parent_id=None,
        )
        db.add(perm)
        created_count += 1
        print(f"  ✓ 新增: {perm_data['code']}")

    db.commit()
    print(f"✓ 权限数据完成 (新增 {created_count} 条)\n")


def seed_role_permissions(db):
    """将所有权限分配给 ADMIN 角色"""
    print("=== 分配角色权限 (ADMIN) ===")

    admin_role = db.query(Role).filter(Role.role_code == "ADMIN").first()
    if not admin_role:
        print("  ✗ ADMIN 角色不存在，请先运行 init_db.py\n")
        return

    all_perms = db.query(Permission).all()
    created_count = 0
    for perm in all_perms:
        existing = (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id == admin_role.id,
                RolePermission.permission_id == perm.id,
            )
            .first()
        )
        if existing:
            print(f"  - 已分配: {perm.code}")
            continue

        rp = RolePermission(role_id=admin_role.id, permission_id=perm.id)
        db.add(rp)
        created_count += 1
        print(f"  ✓ 分配: {perm.code} → ADMIN")

    db.commit()
    print(f"✓ 角色权限分配完成 (新增 {created_count} 条)\n")


def seed_operation_logs(db):
    """插入一些示例操作日志"""
    print("=== 插入操作日志 ===")

    # 查找 admin 用户
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        print("  ✗ admin 用户不存在，跳过日志\n")
        return

    # 检查是否已有日志
    existing_count = db.query(OperationLog).count()
    if existing_count > 0:
        print(f"  - 已有 {existing_count} 条日志，跳过\n")
        return

    sample_logs = [
        {"action": "login", "method": "POST", "path": "/auth/login", "status_code": 200, "success": 1},
        {"action": "get_users", "method": "GET", "path": "/users", "status_code": 200, "success": 1},
        {"action": "create_user", "method": "POST", "path": "/users", "status_code": 200, "success": 1},
        {"action": "get_roles", "method": "GET", "path": "/roles", "status_code": 200, "success": 1},
        {"action": "create_role", "method": "POST", "path": "/roles", "status_code": 200, "success": 1},
        {"action": "update_role", "method": "PUT", "path": "/roles/1", "status_code": 200, "success": 1},
        {"action": "get_permissions", "method": "GET", "path": "/permissions", "status_code": 200, "success": 1},
        {"action": "create_permission", "method": "POST", "path": "/permissions", "status_code": 200, "success": 1},
        {"action": "delete_user", "method": "DELETE", "path": "/users/5", "status_code": 404, "success": 0},
        {"action": "login_failed", "method": "POST", "path": "/auth/login", "status_code": 401, "success": 0},
    ]

    now = datetime.now()
    for i, log_data in enumerate(sample_logs):
        log = OperationLog(
            user_id=admin_user.id,
            action=log_data["action"],
            method=log_data["method"],
            path=log_data["path"],
            ip="127.0.0.1",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            status_code=log_data["status_code"],
            success=log_data["success"],
            latency_ms=random.randint(5, 300),
            created_at=now - timedelta(hours=len(sample_logs) - i),
        )
        db.add(log)
        print(f"  ✓ 日志: [{log_data['method']}] {log_data['path']}")

    db.commit()
    print(f"✓ 操作日志完成 (新增 {len(sample_logs)} 条)\n")


def main():
    print("=" * 60)
    print("种子数据初始化")
    print("=" * 60 + "\n")

    db = SessionLocal()
    try:
        seed_permissions(db)
        seed_role_permissions(db)
        seed_operation_logs(db)
    finally:
        db.close()

    print("=" * 60)
    print("✓ 种子数据插入完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
