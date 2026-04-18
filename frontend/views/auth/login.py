import streamlit as st
import requests
from streamlit_cookies_manager import EncryptedCookieManager

from utils.auth_utils import set_token_cookie

# 后端 API 地址
API_BASE_URL = "http://localhost:8000"


def _handle_login_attempt(cookies: EncryptedCookieManager, username: str, password: str) -> bool:
    """
    调用后端 API 验证用户登录。
    """
    if not username or not password:
        st.error("请输入用户名和密码")
        return False

    try:
        # 构建请求头，携带浏览器端局域网 IP
        headers = {"Content-Type": "application/json"}
        client_ip = st.session_state.get("client_ip", "")
        if client_ip:
            headers["X-Client-IP"] = client_ip

        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": password},
            headers=headers,
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.logged_in = True
            st.session_state.username = data["username"]
            st.session_state.access_token = data["access_token"]
            st.session_state.role = data["role"]
            st.session_state.is_superuser = data["is_superuser"]

            # 将登录信息持久化到浏览器 cookie
            set_token_cookie(
                cookies,
                token=data["access_token"],
                username=data["username"],
                role=data["role"],
                is_superuser=data["is_superuser"],
            )
            return True
        else:
            detail = response.json().get("detail", "用户名或密码错误")
            st.error(detail)
            return False
    except requests.exceptions.ConnectionError:
        st.error("无法连接到后端服务，请检查后端是否启动")
        return False
    except Exception as e:
        st.error(f"登录异常: {e}")
        return False


def show_login_page(cookies: EncryptedCookieManager):
    """显示登录页面"""

    # 隐藏 Streamlit 默认元素，注入左侧固定装饰面板 + 右侧表单样式
    st.markdown("""
    <style>
        /* ===== 隐藏 Streamlit 默认元素 ===== */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        .stApp > header {display: none;}

        /* ===== Streamlit 内容区域推到右侧 ===== */
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }

        section[data-testid="stSidebar"] {
            display: none;
        }

        /* 让 Streamlit 主内容区在右侧 55% 区域显示 */
        .stMainBlockContainer {
            position: fixed !important;
            top: 0 !important;
            right: 0 !important;
            width: 55% !important;
            height: 100vh !important;
            padding: 0 !important;
            max-width: none !important;
            z-index: 1000;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: #ffffff !important;
        }

        /* ===== 左侧装饰面板（纯 HTML，固定定位） ===== */
        .left-panel {
            position: fixed;
            top: 0;
            left: 0;
            width: 45%;
            height: 100vh;
            background: linear-gradient(135deg, #1a0a2e 0%, #4a1a6b 50%, #2d1b69 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            z-index: 998;
        }

        /* 背景动态光效 */
        .left-panel::before {
            content: '';
            position: absolute;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(192, 132, 252, 0.15) 0%, transparent 70%);
            top: 10%;
            left: -10%;
            animation: float-glow 8s ease-in-out infinite;
        }

        .left-panel::after {
            content: '';
            position: absolute;
            width: 250px;
            height: 250px;
            background: radial-gradient(circle, rgba(255, 107, 157, 0.12) 0%, transparent 70%);
            bottom: 15%;
            right: -5%;
            animation: float-glow 6s ease-in-out infinite reverse;
        }

        @keyframes float-glow {
            0%, 100% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(30px, -20px) scale(1.1); }
        }

        /* ===== Logo ===== */
        .logo-area {
            position: absolute;
            top: 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 10;
        }

        .logo-icon {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
            box-shadow: 0 8px 25px rgba(238, 90, 90, 0.4);
            transition: transform 0.3s ease;
        }

        .logo-icon:hover {
            transform: scale(1.05);
        }

        .logo-icon svg {
            width: 35px;
            height: 35px;
            fill: white;
        }

        .logo-text {
            color: white;
            font-size: 20px;
            font-weight: 500;
            letter-spacing: 2px;
        }

        /* ===== SVG 插图 ===== */
        .illustration {
            width: 80%;
            max-width: 500px;
            height: auto;
            margin-top: 80px;
            filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.3));
        }

        /* ===== 登录表单样式 ===== */
        .login-form-title {
            font-size: 26px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 8px;
        }

        .login-form-subtitle {
            font-size: 14px;
            color: #888;
            margin-bottom: 36px;
        }

        .field-label {
            font-size: 14px;
            color: #555;
            margin-bottom: 6px;
            margin-top: 18px;
            font-weight: 500;
        }

        /* 美化输入框 */
        .stTextInput > div > div > input {
            border-radius: 8px !important;
            border: 1.5px solid #e0e0e0 !important;
            padding: 10px 14px !important;
            font-size: 14px !important;
            transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: #7c3aed !important;
            box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1) !important;
        }

        /* 美化登录按钮 */
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            margin-top: 28px !important;
            letter-spacing: 1px !important;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #6d28d9 0%, #9333ea 100%) !important;
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.35) !important;
            transform: translateY(-1px) !important;
        }

        .stButton > button:active {
            transform: translateY(0) !important;
        }

        /* ===== 响应式 ===== */
        @media (max-width: 900px) {
            .left-panel {
                display: none;
            }
            .stMainBlockContainer {
                width: 100% !important;
                left: 0 !important;
            }
        }
    </style>

    <!-- 左侧装饰面板 -->
    <div class="left-panel">
        <div class="logo-area">
            <div class="logo-icon">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                </svg>
            </div>
            <div class="logo-text">数据中台</div>
        </div>
        <svg class="illustration" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
            <!-- 背景光圈 -->
            <circle cx="200" cy="150" r="120" fill="rgba(255,255,255,0.05)"/>
            <circle cx="200" cy="150" r="90" fill="rgba(255,255,255,0.08)"/>
            <!-- 主屏幕 -->
            <rect x="120" y="80" width="160" height="100" rx="8" fill="#2d1b4e" stroke="#ff6b9d" stroke-width="2"/>
            <rect x="130" y="90" width="140" height="80" rx="4" fill="#1a0a2e"/>
            <!-- 折线图 -->
            <polyline points="140,150 160,130 180,140 200,110 220,120 240,100 260,90"
                      fill="none" stroke="#ff6b9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="140" cy="150" r="4" fill="#ff6b9d"/>
            <circle cx="160" cy="130" r="4" fill="#ff6b9d"/>
            <circle cx="180" cy="140" r="4" fill="#ff6b9d"/>
            <circle cx="200" cy="110" r="4" fill="#ff6b9d"/>
            <circle cx="220" cy="120" r="4" fill="#ff6b9d"/>
            <circle cx="240" cy="100" r="4" fill="#ff6b9d"/>
            <circle cx="260" cy="90" r="4" fill="#ff6b9d"/>
            <!-- 柱状图 -->
            <rect x="140" y="160" width="15" height="10" fill="#c084fc" opacity="0.8"/>
            <rect x="165" y="155" width="15" height="15" fill="#c084fc" opacity="0.8"/>
            <rect x="190" y="145" width="15" height="25" fill="#c084fc" opacity="0.8"/>
            <rect x="215" y="150" width="15" height="20" fill="#c084fc" opacity="0.8"/>
            <rect x="240" y="140" width="15" height="30" fill="#c084fc" opacity="0.8"/>
            <!-- 底座 -->
            <rect x="180" y="180" width="40" height="8" rx="2" fill="#4a4a6a"/>
            <rect x="190" y="188" width="20" height="15" rx="2" fill="#4a4a6a"/>
            <rect x="170" y="203" width="60" height="6" rx="3" fill="#4a4a6a"/>
            <!-- 装饰粒子 -->
            <circle cx="80" cy="100" r="3" fill="#ff6b9d" opacity="0.6"/>
            <circle cx="320" cy="120" r="4" fill="#c084fc" opacity="0.6"/>
            <circle cx="90" cy="200" r="5" fill="#ff6b9d" opacity="0.4"/>
            <circle cx="310" cy="180" r="3" fill="#c084fc" opacity="0.5"/>
            <circle cx="70" cy="150" r="2" fill="#ff6b9d" opacity="0.7"/>
            <circle cx="330" cy="160" r="4" fill="#c084fc" opacity="0.4"/>
            <!-- 文字标签 -->
            <text x="100" y="80" fill="#ff6b9d" font-size="10" opacity="0.7">Data</text>
            <text x="300" y="90" fill="#c084fc" font-size="10" opacity="0.7">AI</text>
            <text x="310" y="220" fill="#ff6b9d" font-size="10" opacity="0.7">Analytics</text>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    # ===== 登录表单（Streamlit 原生组件，显示在右侧区域） =====
    # 水平居中：左留白 | 表单 | 右留白
    col_left, col_form, col_right = st.columns([0.8, 2, 0.8])

    with col_form:
        # 垂直间距
        st.markdown("<br><br><br>", unsafe_allow_html=True)

        # 标题
        st.markdown('<div class="login-form-title">欢迎使用数据中台</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-form-subtitle">请登录您的账户以继续</div>', unsafe_allow_html=True)

        # 用户名
        st.markdown('<p class="field-label">用户名</p>', unsafe_allow_html=True)
        username = st.text_input(
            "username",
            placeholder="请输入用户名",
            label_visibility="collapsed",
            key="login_username_input",
        )

        # 密码
        st.markdown('<p class="field-label">密码</p>', unsafe_allow_html=True)
        password = st.text_input(
            "password",
            type="password",
            placeholder="请输入密码",
            label_visibility="collapsed",
            key="login_password_input",
        )

        # 登录按钮
        login_clicked = st.button("登 录", key="login_button", width="stretch")

        if login_clicked:
            if _handle_login_attempt(cookies, username, password):
                st.success("✅ 登录成功，系统加载中...")
