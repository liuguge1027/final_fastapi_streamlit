"""
普通用户主界面
============
USER 角色的主界面
"""
import streamlit as st
from utils.router import list_subpages, load_subpage
from utils.auth_utils import logout, get_user_role


def show_role_page(cookies):
    """
    显示普通用户主界面。

    Args:
        cookies: EncryptedCookieManager 实例
    """
    role = get_user_role()

    # ===== 侧边栏 =====
    with st.sidebar:
        st.markdown("# 👤 用户中心")
        st.markdown(f"**{st.session_state.get('username', '用户')}**")
        st.markdown(f"🏷️ 角色: `{role}`")
        st.divider()

        # 获取子页面列表
        subpages = list_subpages(role)

        if subpages:
            st.markdown("## 📋 功能菜单")
            # 创建页面选择器
            page_names = [name for _, name in subpages]
            if "current_page" not in st.session_state:
                st.session_state.current_page = page_names[0] if page_names else None

            selected_page = st.radio(
                "选择页面",
                page_names,
                index=page_names.index(st.session_state.current_page) if st.session_state.current_page in page_names else 0,
                label_visibility="collapsed"
            )
            st.session_state.current_page = selected_page
        else:
            st.info("暂无功能页面")

        st.divider()

        # 退出登录按钮
        if st.button("🚪 退出登录", type="primary", use_container_width=True):
            logout(cookies)
            st.rerun()

    # ===== 主内容区域 =====
    if subpages and st.session_state.current_page:
        # 找到选中的页面文件名
        selected_file = next(
            (file for file, name in subpages if name == st.session_state.current_page),
            None
        )
        if selected_file:
            # 加载子页面
            load_subpage(role, selected_file)
    else:
        # 默认欢迎页面
        st.title("🏠 用户中心")
        st.success(f"欢迎回来，{st.session_state.get('username', '用户')}！")
        st.info("请从侧边栏选择功能模块开始使用。")
