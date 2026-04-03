"""
统一侧边栏模板
==============
根据角色渲染侧边栏菜单，返回用户选择的 (主菜单, 子菜单)。
菜单结构由 ROLE_MENUS 字典集中管理。
"""
import streamlit as st
from utils.auth_utils import logout
from utils.api_client import api_get


import time

def get_role_menus() -> dict:
    """
    通过接口动态从数据库拉取角色菜单配置
    （附带缓存 10 秒防重复请求机制）
    """
    cache_key = "role_menus_cache"
    time_key = "role_menus_cache_time"
    now = time.time()
    
    try:
        if cache_key not in st.session_state or (now - st.session_state.get(time_key, 0) > 10):
            res = api_get("/role-menus")
            st.session_state[cache_key] = res if res else {}
            st.session_state[time_key] = now
            
        return st.session_state[cache_key]
    except Exception as e:
        st.sidebar.error(f"拉取异常: {e}")
        return {}

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
    
    # 动态获取角色菜单配置
    role_menus_dict = get_role_menus()
    
    # 如果是 admin，默认合并赋予所有角色的可用菜单
    if role_lower == "admin":
        menus = {}
        for r, r_menus in role_menus_dict.items():
            for main_menu, sub_menus in r_menus.items():
                if main_menu not in r_menus:
                    continue
                if main_menu not in menus:
                    menus[main_menu] = []
                
                # sub_menus is now a list of dicts: [{"sub_menu": "...", "module_path": "..."}, ...]
                existing_sub_names = [m["sub_menu"] for m in menus[main_menu]]
                for sub_item in sub_menus:
                    if sub_item["sub_menu"] not in existing_sub_names:
                        menus[main_menu].append(sub_item)
    else:
        menus = role_menus_dict.get(role_lower, {})
        
    title = ROLE_TITLES.get(role_lower, f"{role}")

    with st.sidebar:
        st.markdown(f"##  {title}：👤{st.session_state.get('username', '用户')} ##")
        if not menus:
            st.warning("暂无可用菜单")
            if st.button("退出登录", type="primary", use_container_width=True):
                logout(cookies)
                st.success("正在退出...")
                return None, None
            return None, None

        # 主菜单选择
        main_menu_options = list(menus.keys())
        main_menu = st.selectbox(
            "📂 功能模块",
            main_menu_options,
            key="sidebar_main_menu",
        )

        # 子菜单选择 (menus[main_menu] is a list of dicts)
        sub_menu_list = menus.get(main_menu, [])
        sub_menu_names = [m["sub_menu"] for m in sub_menu_list]
        
        sub_menu = st.radio(
            "📄 页面",
            sub_menu_names,
            key="sidebar_sub_menu",
            label_visibility="collapsed",
        )


        if st.button("退出登录", type="primary", use_container_width=True):
            logout(cookies)
            st.success("正在退出...")
            return None, None
        st.markdown(f"角色: {role}")
    # 保存当前可用的菜单结构到 session_state，供 page_registry.py 使用
    st.session_state["active_menus"] = menus
    
    return main_menu, sub_menu
