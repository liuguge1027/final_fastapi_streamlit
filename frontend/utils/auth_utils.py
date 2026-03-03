"""
前端登录持久化工具模块
=======================
使用 streamlit-cookies-manager 将 JWT 和用户信息加密存储到浏览器 cookie，
实现页面刷新 / 关闭后重新打开仍保持登录状态。

核心函数:
    - init_cookie_manager() : 初始化加密 Cookie 管理器（单例）
    - set_token_cookie()    : 登录成功后写入 cookie
    - get_token_cookie()    : 从 cookie 读取已保存的登录信息
    - check_login()         : 自动从 cookie 恢复到 session_state
    - logout()              : 清除 cookie 和 session_state
"""

import os
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager


# ===== Cookie 键名常量 =====
_COOKIE_KEY_TOKEN = "access_token"
_COOKIE_KEY_USERNAME = "username"
_COOKIE_KEY_ROLE = "role"
_COOKIE_KEY_IS_SUPERUSER = "is_superuser"

# Cookie 加密密钥（仅用于浏览器端加密，与后端 JWT secret 无关）
_COOKIE_PASSWORD = os.environ.get("COOKIE_SECRET", "my-streamlit-cookie-secret-key-2026")


def init_cookie_manager() -> EncryptedCookieManager:
    """
    初始化并返回 EncryptedCookieManager 单例。

    必须在 Streamlit 页面最顶部（`st.set_page_config` 之后）调用一次，
    并且在 cookies 尚未就绪时提前 `st.stop()`。

    Returns:
        EncryptedCookieManager: 已就绪的 cookie 管理器实例。
    """
    cookies = EncryptedCookieManager(
        prefix="datahub_",       # 所有 cookie 键名添加前缀，避免冲突
        password=_COOKIE_PASSWORD,
    )

    if not cookies.ready():
        # 首次渲染时，cookie manager 需要通过前端 JS 读取浏览器 cookie
        # 此时尚未就绪，必须 stop 并等待下一轮渲染
        st.stop()

    return cookies


def set_token_cookie(
    cookies: EncryptedCookieManager,
    token: str,
    username: str,
    role: str,
    is_superuser: bool,
) -> None:
    """
    登录成功后，将 JWT 和用户信息写入浏览器 cookie。

    Args:
        cookies: 已初始化的 cookie 管理器。
        token: 后端返回的 JWT access_token。
        username: 用户名。
        role: 用户角色 (如 "admin", "user")。
        is_superuser: 是否为超级管理员。
    """
    cookies[_COOKIE_KEY_TOKEN] = token
    cookies[_COOKIE_KEY_USERNAME] = username
    cookies[_COOKIE_KEY_ROLE] = role
    cookies[_COOKIE_KEY_IS_SUPERUSER] = "1" if is_superuser else "0"
    cookies.save()  # 将更改同步到浏览器


def get_token_cookie(cookies: EncryptedCookieManager) -> dict | None:
    """
    从 cookie 中读取已保存的登录信息。

    Returns:
        dict: 包含 access_token, username, role, is_superuser 的字典；
              如果 cookie 中没有有效 token 则返回 None。
    """
    token = cookies.get(_COOKIE_KEY_TOKEN, "")
    if not token:
        return None

    return {
        "access_token": token,
        "username": cookies.get(_COOKIE_KEY_USERNAME, ""),
        "role": cookies.get(_COOKIE_KEY_ROLE, ""),
        "is_superuser": cookies.get(_COOKIE_KEY_IS_SUPERUSER, "0") == "1",
    }


def check_login(cookies: EncryptedCookieManager) -> bool:
    """
    检查登录状态：优先使用 session_state，其次尝试从 cookie 恢复。

    此函数可在每个业务页面顶部统一调用，一行即可完成登录校验：
        >>> if not check_login(cookies):
        ...     st.stop()

    Returns:
        bool: 当前是否处于已登录状态。
    """
    # 1. session_state 已有登录态 → 直接返回
    if st.session_state.get("logged_in", False):
        return True

    # 2. 尝试从 cookie 恢复
    saved = get_token_cookie(cookies)
    if saved and saved["access_token"]:
        st.session_state.logged_in = True
        st.session_state.access_token = saved["access_token"]
        st.session_state.username = saved["username"]
        st.session_state.role = saved["role"]
        st.session_state.is_superuser = saved["is_superuser"]
        return True

    # 3. 无有效登录信息
    return False


def logout(cookies: EncryptedCookieManager) -> None:
    """
    退出登录：清除浏览器 cookie 和 session_state 中的所有登录信息。

    调用后应紧接 `st.rerun()` 以刷新页面回到登录界面。
    """
    # 清除 cookiekey
    for key in [_COOKIE_KEY_TOKEN, _COOKIE_KEY_USERNAME, _COOKIE_KEY_ROLE, _COOKIE_KEY_IS_SUPERUSER]:
        cookies[key] = ""
    cookies.save()

    # 清除 session_state
    for key in ["logged_in", "access_token", "username", "role", "is_superuser", "current_page"]:
        st.session_state.pop(key, None)


def get_user_role() -> str:
    """
    获取当前登录用户的角色。

    Returns:
        str: 用户角色，如 "ADMIN", "MANAGER", "USER"；未登录返回空字符串。
    """
    if not st.session_state.get("logged_in", False):
        return ""
    return st.session_state.get("role", "")
