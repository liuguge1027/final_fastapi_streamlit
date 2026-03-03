"""
路由管理器
==========
根据登录状态和用户角色动态加载对应的页面。
"""
import os
import importlib.util
import streamlit as st
from typing import Optional
from pathlib import Path


def get_views_dir() -> Path:
    """获取 views 目录的绝对路径"""
    return Path(__file__).parent.parent / "views"


def route_app(cookies) -> None:
    """
    统一路由函数：根据登录状态和角色加载对应页面。

    Args:
        cookies: EncryptedCookieManager 实例。
    """
    from utils.auth_utils import check_login, get_user_role

    # 检查登录状态
    if not check_login(cookies):
        # 未登录 → 加载登录页
        load_login_page(cookies)
        return

    # 已登录 → 根据角色加载对应主界面
    role = get_user_role()
    if not role:
        # 如果角色为空，默认使用 USER
        role = "USER"

    # 尝试加载对应角色的主界面
    try:
        load_role_index(role, cookies)
    except Exception as e:
        st.error(f"加载页面失败: {e}")
        st.info(f"角色 '{role}' 页面不存在，请检查 views/{role.lower()}/index.py 是否存在")


def load_login_page(cookies) -> None:
    """加载登录页面"""
    from views.auth.login import show_login_page
    show_login_page(cookies)


def load_role_index(role: str, cookies) -> None:
    """
    统一入口：所有角色共用一套 sidebar + page_registry。

    Args:
        role: 用户角色（如 "ADMIN", "MANAGER", "USER"）
        cookies: EncryptedCookieManager 实例
    """
    from ui.sidebar_template import render_sidebar
    from ui.page_registry import route_page

    role_lower = role.lower()

    # 渲染统一侧边栏，返回用户选择的菜单
    main_menu, sub_menu = render_sidebar(role_lower, cookies)

    if main_menu and sub_menu:
        # 根据角色 + 菜单选择，动态加载对应页面
        route_page(role_lower, main_menu, sub_menu)
    elif main_menu is None and sub_menu is None:
        # render_sidebar 返回 None 表示该角色无菜单配置
        st.title("📋 控制台")
        st.info(f"角色 **{role}** 暂无可用菜单，请联系管理员配置权限。")


def list_subpages(role: str) -> list[tuple[str, str]]:
    """
    列出指定角色目录下的所有子页面。

    Args:
        role: 用户角色

    Returns:
        list[tuple[str, str]]: 子页面列表，格式为 [(文件名, 显示名称), ...]
    """
    role_lower = role.lower()
    role_dir = get_views_dir() / role_lower

    if not role_dir.exists():
        return []

    subpages = []
    for file in role_dir.glob("*.py"):
        if file.name == "index.py" or file.name.startswith("_"):
            continue
        # 从文件名生成显示名称（去掉 .py，下划线转空格，首字母大写）
        name = file.stem.replace("_", " ").title()
        subpages.append((file.stem, name))

    return sorted(subpages, key=lambda x: x[1])


def load_subpage(role: str, page_name: str):
    """
    加载指定角色的子页面。

    Args:
        role: 用户角色
        page_name: 子页面名称（不含 .py）
    """
    role_lower = role.lower()
    page_path = get_views_dir() / role_lower / f"{page_name}.py"

    if not page_path.exists():
        st.error(f"页面 '{page_name}' 不存在")
        return

    # 动态导入并加载子页面
    spec = importlib.util.spec_from_file_location(f"views.{role_lower}.{page_name}", page_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "show_page"):
            module.show_page()
        else:
            st.error(f"页面缺少 show_page() 函数")
