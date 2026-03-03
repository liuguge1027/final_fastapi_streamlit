"""
页面注册表
==========
角色 → (主菜单, 子菜单) → 页面模块路径 的映射。
通过 route_page() 动态导入模块并调用 show_page()。
"""
import importlib
import streamlit as st


# =====================================================================
# PAGE_REGISTRY
# 角色 → { (主菜单, 子菜单): "模块路径" }
# 模块路径指向含有 show_page() 函数的 Python 模块
# =====================================================================

PAGE_REGISTRY = {
    "admin": {
        ("系统管理", "用户管理"):     "views.admin.pages.user_page",
        ("系统管理", "角色管理"):     "views.admin.pages.role_page",
        ("系统管理", "权限管理"):     "views.admin.pages.permission_page",
        ("系统管理", "角色权限管理"): "views.admin.pages.role_permission_page",
        ("系统管理", "操作日志"):     "views.admin.pages.operation_log_page",
        ("财务报表", "收入报表"):     "views.finance.pages.income_page",
        ("财务报表", "支出报表"):     "views.finance.pages.expense_page",
        ("销售报表", "销售报表"):     "views.sale.pages.sales_page",
        ("销售报表", "客户报表"):     "views.sale.pages.customer_page",
        ("人力报表", "员工列表"):     "views.hr.pages.employee_page",
        ("人力报表", "绩效考核"):     "views.hr.pages.performance_page",
    },
    "finance": {
        ("财务报表", "收入报表"):     "views.finance.pages.income_page",
        ("财务报表", "支出报表"):     "views.finance.pages.expense_page",
        ("系统管理", "操作日志"):     "views.admin.pages.operation_log_page",
    },
    "sale": {
        ("销售报表", "销售报表"):     "views.sale.pages.sales_page",
        ("销售报表", "客户报表"):     "views.sale.pages.customer_page",
        ("系统管理", "操作日志"):     "views.admin.pages.operation_log_page",
    },
    "hr": {
        ("人力报表", "员工列表"):     "views.hr.pages.employee_page",
        ("人力报表", "绩效考核"):     "views.hr.pages.performance_page",
        ("系统管理", "操作日志"):     "views.admin.pages.operation_log_page",
    },
}


def route_page(role: str, main_menu: str, sub_menu: str) -> None:
    """
    根据角色和菜单选择，动态加载并执行对应页面的 show_page() 函数。

    Args:
        role: 用户角色（小写）
        main_menu: 主菜单名称
        sub_menu: 子菜单名称
    """
    role_lower = role.lower()
    registry = PAGE_REGISTRY.get(role_lower, {})
    module_path = registry.get((main_menu, sub_menu))

    if not module_path:
        st.warning(f"⚠️ 当前角色 **{role}** 无权访问页面：{main_menu} > {sub_menu}")
        return

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        st.error(f"❌ 页面模块 `{module_path}` 未找到，请检查文件是否存在。")
        return
    except Exception as e:
        st.error(f"❌ 加载模块 `{module_path}` 失败: {e}")
        return

    # 调用 show_page()
    if hasattr(module, "show_page"):
        module.show_page()
    else:
        st.error(
            f"❌ 模块 `{module_path}` 缺少 `show_page()` 函数。\n\n"
            f"请在该文件中添加：\n```python\ndef show_page():\n    ...\n```"
        )
