"""
财务模块界面
===========
财务角色的主界面入口
"""
import streamlit as st
from utils.auth_utils import logout, get_user_role


def show_role_page(cookies):
    """
    显示财务模块主界面。

    Args:
        cookies: EncryptedCookieManager 实例
    """
    # 直接从 session_state 获取，更可靠
    role = st.session_state.get("role", "")
    is_superuser = st.session_state.get("is_superuser", False)
    username = st.session_state.get("username", "用户")

    with st.sidebar:
        st.markdown("# 财务控制台")
        st.markdown(f"**{username}**")
        st.markdown(f"角色: `{role}`")
        st.divider()

        if st.button("退出登录", type="primary", use_container_width=True):
            logout(cookies)
            st.rerun()

    st.title("💰 财务模块")
    st.markdown("---")

    # ========================================
    # 显示当前用户信息（先显示，方便调试）
    # ========================================
    with st.expander("🔍 查看当前用户信息（必看！）", expanded=True):
        st.json({
            "username": username,
            "role": role,
            "role_lower": role.lower() if role else "",
            "is_superuser": is_superuser,
            "logged_in": st.session_state.get("logged_in", False)
        })
        st.warning("⚠️ 请确认上面的 role 值是什么！")

    st.markdown("---")

    # ========================================
    # 示例1：只有 ADMIN 角色才能看到的按钮
    # ========================================
    st.subheader("方法1：根据角色显示/隐藏按钮（严格等于）")

    if role == "ADMIN":
        if st.button("🔐 管理员专用按钮 - 方法1", type="primary"):
            st.success("✅ 你是管理员，点击成功！")
            st.balloons()
    else:
        st.info(f"ℹ️ 这个按钮只有角色为 'ADMIN' 才能看到，当前角色是 '{role}'")

    st.markdown("---")

    # ========================================
    # 示例1.5：不区分大小写的判断
    # ========================================
    st.subheader("方法1.5：根据角色显示/隐藏按钮（不区分大小写）")

    if role and role.upper() == "ADMIN":
        if st.button("🔐 管理员专用按钮 - 方法1.5", type="primary"):
            st.success("✅ 你是管理员，点击成功！")
            st.balloons()
    else:
        st.info(f"ℹ️ 这个按钮只有角色为 'admin'（不区分大小写）才能看到，当前角色是 '{role}'")

    st.markdown("---")

    # ========================================
    # 示例2：所有用户都能看到，但只有 admin 能点击
    # ========================================
    st.subheader("方法2：所有用户都能看到，但只有 admin 能点击")

    # 禁用按钮的条件：不是 ADMIN（不区分大小写）且 不是超级管理员
    is_disabled = not (
        (role and role.upper() == "ADMIN") or 
        is_superuser
    )

    if st.button("� 管理员专用按钮 - 方法2", disabled=is_disabled, type="primary"):
        st.success("✅ 你是管理员，点击成功！")
        st.balloons()

    if is_disabled:
        st.warning(f"⚠️ 这个按钮只有管理员才能点击，当前角色是 '{role}'")

    st.markdown("---")

    # ========================================
    # 示例3：根据 is_superuser 判断
    # ========================================
    st.subheader("方法3：根据超级管理员标志判断")

    if is_superuser:
        if st.button("👑 超级管理员专用按钮", type="primary"):
            st.success("✅ 你是超级管理员，点击成功！")
            st.snow()
    else:
        st.info("ℹ️ 这个按钮只有超级管理员才能看到")
