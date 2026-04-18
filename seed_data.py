#!/usr/bin/env python3
"""
种子数据初始化脚本
================
插入角色菜单、操作日志的初始数据。

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
from backend.models.operation_log import OperationLog
from backend.models.role_menu import RoleMenu


# =====================================================================
# 角色菜单种子数据
# =====================================================================
ROLE_MENUS = {
    "admin": {
        "系统管理": [
            ("用户管理", "views.admin.pages.user_page"),
            ("角色管理", "views.admin.pages.role_page"),
            ("菜单管理", "views.admin.role_menus"),
            ("操作日志", "views.admin.pages.operation_log_page"),
        ],
        "财务报表": [
            ("收入报表", "views.finance.pages.income_page"),
            ("支出报表", "views.finance.pages.expense_page"),
        ],
        "销售报表": [
            ("销售报表", "views.sale.pages.sales_page"),
            ("客户报表", "views.sale.pages.customer_page"),
        ],
        "人力报表": [
            ("员工列表", "views.hr.pages.employee_page"),
            ("绩效考核", "views.hr.pages.performance_page"),
        ],
    },
    "finance": {
        "系统管理": [
            ("操作日志", "views.admin.pages.operation_log_page"),
        ],
        "财务报表": [
            ("收入报表", "views.finance.pages.income_page"),
            ("支出报表", "views.finance.pages.expense_page"),
        ],
    },
    "sale": {
        "系统管理": [
            ("操作日志", "views.admin.pages.operation_log_page"),
        ],
        "销售报表": [
            ("销售报表", "views.sale.pages.sales_page"),
            ("客户报表", "views.sale.pages.customer_page"),
        ],
    },
    "hr": {
        "系统管理": [
            ("角色管理", "views.admin.pages.role_page"),
            ("操作日志", "views.admin.pages.operation_log_page"),
        ],
        "人力报表": [
            ("员工列表", "views.hr.pages.employee_page"),
            ("绩效考核", "views.hr.pages.performance_page"),
        ],
    },
}


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
        {"action": "用户登录", "method": "POST", "path": "/auth/login", "status_code": 200, "success": 1},
        {"action": "创建用户", "method": "POST", "path": "/users", "status_code": 200, "success": 1},
        {"action": "编辑用户", "method": "PUT", "path": "/users/2", "status_code": 200, "success": 1},
        {"action": "创建角色", "method": "POST", "path": "/roles", "status_code": 200, "success": 1},
        {"action": "编辑角色", "method": "PUT", "path": "/roles/1", "status_code": 200, "success": 1},
        {"action": "创建菜单映射", "method": "POST", "path": "/role-menus", "status_code": 200, "success": 1},
        {"action": "删除用户", "method": "DELETE", "path": "/users/5", "status_code": 404, "success": 0},
        {"action": "用户登录", "method": "POST", "path": "/auth/login", "status_code": 401, "success": 0},
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


def seed_role_menus(db):
    """插入角色菜单种子数据"""
    print("=== 插入角色菜单数据 ===")
    try:
        # 先清空已有数据
        db.query(RoleMenu).delete()
        
        for role_code, menus in ROLE_MENUS.items():
            global_sort_order = 1
            for main_menu, sub_menu_list in menus.items():
                for menu_info in sub_menu_list:
                    
                    if isinstance(menu_info, tuple):
                        sub_menu, module_path = menu_info
                    else:
                        sub_menu, module_path = menu_info, None
                    
                    rm = RoleMenu(
                        role_code=role_code,
                        main_menu=main_menu,
                        sub_menu=sub_menu,
                        module_path=module_path,
                        sort_order=global_sort_order
                    )
                    global_sort_order += 1
                    db.add(rm)
        
        db.commit()
        print("✓ 角色菜单数据完成\n")
    except Exception as e:
        db.rollback()
        print(f"  ✗ 角色菜单数据失败: {e}\n")


def main():
    print("=" * 60)
    print("种子数据初始化")
    print("=" * 60 + "\n")

    db = SessionLocal()
    try:
        seed_operation_logs(db)
        seed_role_menus(db)
    finally:
        db.close()

    print("=" * 60)
    print("✓ 种子数据插入完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
