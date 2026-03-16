"""
客户端 IP 获取工具
========================
通过 Streamlit 运行时获取浏览器客户端的真实 IP，
当检测到 127.0.0.1 时自动回退到本机局域网 IP。
结果缓存到 st.session_state.client_ip。
"""
import socket
import streamlit as st


def get_client_ip() -> str:
    """
    获取客户端 IP 地址（优先真实远端 IP，回退本机局域网 IP）。

    首次调用时探测并缓存到 session_state，后续直接返回。

    Returns:
        str: IP 地址字符串，获取失败时为空字符串。
    """
    # 已缓存则直接返回
    if st.session_state.get("client_ip"):
        return st.session_state.client_ip

    ip = ""

    # ── 方法 1: 反向代理 / CDN 头（如 Nginx 设置了 X-Forwarded-For） ──
    try:
        headers = st.context.headers
        for header_name in ("X-Forwarded-For", "X-Real-Ip"):
            val = headers.get(header_name)
            if val:
                ip = val.split(",")[0].strip()
                break
    except Exception:
        pass

    # ── 方法 2: Streamlit 运行时 → WebSocket 客户端真实 IP ──
    if not ip or ip in ("127.0.0.1", "::1"):
        ip = _get_streamlit_remote_ip() or ip

    # ── 方法 3: 仍然是 127.0.0.1 → 用 socket 获取本机局域网 IP ──
    if not ip or ip in ("127.0.0.1", "::1"):
        ip = _get_local_lan_ip() or ip

    st.session_state.client_ip = ip or ""
    return st.session_state.client_ip


def _get_streamlit_remote_ip() -> str:
    """尝试从 Streamlit 内部运行时获取 WebSocket 连接的远端 IP。"""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        from streamlit.runtime import get_instance

        ctx = get_script_run_ctx()
        if ctx is None:
            return ""

        runtime_inst = get_instance()

        # 尝试通过 session manager 获取 session info
        session_mgr = getattr(runtime_inst, "_session_mgr", None)
        if session_mgr is None:
            return ""

        # Streamlit 不同版本方法名不同，依次尝试
        for method_name in (
            "get_active_session_info",
            "get_session_info",
        ):
            method = getattr(session_mgr, method_name, None)
            if method is None:
                continue
            try:
                session_info = method(ctx.session_id)
                if session_info is None:
                    continue
                client = getattr(session_info, "client", None)
                if client is None:
                    continue
                request = getattr(client, "request", None)
                if request is None:
                    continue
                remote_ip = getattr(request, "remote_ip", None)
                if remote_ip:
                    return remote_ip
            except Exception:
                continue
    except Exception:
        pass

    return ""


def _get_local_lan_ip() -> str:
    """
    获取本机在局域网中的 IP 地址。

    通过创建一个 UDP socket 并 "连接" 到外部地址来确定
    操作系统选择的出口网卡 IP（不会实际发送数据）。
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # 不会真正发送数据，只是让 OS 选择出口网卡
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        pass

    # 回退方案：通过 hostname 解析
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip and ip != "127.0.0.1":
            return ip
    except Exception:
        pass

    return ""
