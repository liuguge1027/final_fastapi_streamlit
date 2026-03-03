"""
Streamlit 应用入口文件
====================
仅作为入口文件，不包含业务逻辑。
"""
import streamlit as st
from utils.auth_utils import init_cookie_manager
from utils.router import route_app
cookies = init_cookie_manager()
# ===== 页面配置（必须是第一个 Streamlit 命令） =====
st.set_page_config(
    page_title="数据中台",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
route_app(cookies)
