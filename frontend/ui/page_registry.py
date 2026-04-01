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

def route_page(role: str, main_menu: str, sub_menu: str) -> None:
    """
    根据角色和菜单选择，从 session_state['active_menus'] 中找到对应的 module_path 并加载。
    """
    active_menus = st.session_state.get("active_menus", {})
    sub_menu_list = active_menus.get(main_menu, [])
    
    # 查找匹配的子菜单项
    module_path = None
    for item in sub_menu_list:
        if item.get("sub_menu") == sub_menu:
            module_path = item.get("module_path")
            break

    if not module_path:
        st.warning(f"⚠️ 无法找到页面模块映射：{main_menu} > {sub_menu}")
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
