"""
统一侧边栏模板
==============
根据角色渲染侧边栏菜单，返回用户选择的 (主菜单, 子菜单)。
菜单结构由 ROLE_MENUS 字典集中管理。
"""
import streamlit as st
from utils.auth_utils import logout


# =====================================================================
# 角色菜单配置
# key = 角色编码 (小写)
# value = OrderedDict{主菜单名: [子菜单列表]}
# =====================================================================

ROLE_MENUS = {
    "admin": {
        "系统管理": ["用户管理", "角色管理", "权限管理", "角色权限管理", "操作日志"],
        "财务报表": ["收入报表", "支出报表"],
        "销售报表": ["销售报表", "客户报表"],
        "人力报表": ["员工列表", "绩效考核"],
    },
    "finance": {
        "财务报表": ["收入报表", "支出报表"],
        "系统管理": ["操作日志"],
    },
    "sale": {
        "销售报表": ["销售报表", "客户报表"],
        "系统管理": ["操作日志"],
    },
    "hr": {
        "人力报表": ["员工列表", "绩效考核"],
        "系统管理": ["操作日志"],
    },
}

# 角色显示标题
ROLE_TITLES = {
    "admin":   "🛡️ 管理员",
    "finance": "💰 财务",
    "sale":    "📈 销售",
    "hr":      "👥 人力",
}


def render_sidebar(role: str, cookies) -> tuple:
    """
    渲染统一侧边栏并返回用户选择的菜单。

    Args:
        role: 当前用户角色（小写，如 "admin"）
        cookies: EncryptedCookieManager 实例

    Returns:
        tuple: (main_menu, sub_menu)，用户当前选中的主菜单和子菜单
    """
    role_lower = role.lower()
    menus = ROLE_MENUS.get(role_lower, {})
    title = ROLE_TITLES.get(role_lower, f"{role}")

    with st.sidebar:
        st.markdown(f"##  {title}：👤{st.session_state.get('username', '用户')} ##")
        if not menus:
            st.warning("暂无可用菜单")
            if st.button("退出登录", type="primary", use_container_width=True):
                logout(cookies)
                st.rerun()
            return None, None

        # 主菜单选择
        main_menu_options = list(menus.keys())
        main_menu = st.selectbox(
            "📂 功能模块",
            main_menu_options,
            key="sidebar_main_menu",
        )

        # 子菜单选择
        sub_menu_options = menus.get(main_menu, [])
        sub_menu = st.radio(
            "📄 页面",
            sub_menu_options,
            key="sidebar_sub_menu",
            label_visibility="collapsed",
        )


        if st.button("退出登录", type="primary", use_container_width=True):
            logout(cookies)
            st.rerun()
        st.markdown(f"角色: {role}")
    return main_menu, sub_menu
