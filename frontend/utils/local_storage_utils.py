"""
手机端登录持久化工具 - localStorage 读写
==========================================
作为 Cookie 方案的手机端兜底，解决手机浏览器 Cookie 限制问题。
由 auth_utils.py 的 set_token_cookie / check_login / logout 内部调用。
不需要修改除 auth_utils.py 之外的任何其他文件。
"""
import json
import time
import streamlit as st

try:
    from streamlit_js_eval import streamlit_js_eval as _js_eval
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

_LS_KEY = "datahub_auth"  # localStorage 存储的键名


def save_auth_to_local_storage(token: str, username: str, role: str, is_superuser: bool) -> None:
    """将登录信息写入 localStorage（优先写入 parent 以应对手机端 iframe 限制）。"""
    if not _AVAILABLE:
        return
    try:
        payload = json.dumps({
            "token": token,
            "username": username,
            "role": role,
            "is_superuser": is_superuser,
        })
        js_payload = json.dumps(payload)
        
        js_expr = f"""
        (()=>{{
            try {{
                var storage = null;
                try {{ storage = window.parent.localStorage; }} catch(e) {{}}
                if (!storage) {{ storage = window.localStorage || localStorage; }}
                storage.setItem('{_LS_KEY}', {js_payload});
            }} catch(e) {{}}
            return 1;
        }})()
        """
        
        _js_eval(
            js_expressions=js_expr,
            key=f"_ls_save_{int(time.time() * 1000)}",
        )
    except Exception:
        pass

def load_auth_from_local_storage() -> dict | None:
    """
    从 localStorage 读取登录信息。

    Returns:
        None  → JS 尚未执行（首次渲染），调用方应 st.stop() 等待下一轮
        {}    → localStorage 中无数据
        dict  → 包含 token / username / role / is_superuser 的字典
    """
    if not _AVAILABLE:
        return {}
    try:
        # nonce 随 logout 变化，保证退出后强制重新读取，不会读到旧缓存
        nonce = st.session_state.get("_ls_nonce", 0)
        js_expr = f"""
        (()=>{{
            try {{
                var storage = null;
                try {{ storage = window.parent.localStorage; }} catch(e) {{}}
                if (!storage) {{ storage = window.localStorage || localStorage; }}
                var v = storage.getItem('{_LS_KEY}');
                return v !== null ? v : '__EMPTY__';
            }} catch(e) {{
                return '__EMPTY__';
            }}
        }})()
        """
        result = _js_eval(
            js_expressions=js_expr,
            key=f"_ls_load_{nonce}",
        )
        if result is None:
            return None       # JS 尚未执行，等待 rerun
        if result == "__EMPTY__":
            return {}         # localStorage 为空
        data = json.loads(result)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def clear_auth_from_local_storage() -> None:
    """清除 localStorage 中的登录信息，并更新 nonce 使下次强制重新读取。"""
    if not _AVAILABLE:
        return
    try:
        js_expr = f"""
        (()=>{{
            try {{
                var storage = null;
                try {{ storage = window.parent.localStorage; }} catch(e) {{}}
                if (!storage) {{ storage = window.localStorage || localStorage; }}
                storage.removeItem('{_LS_KEY}');
            }} catch(e) {{}}
            return 1;
        }})()
        """
        _js_eval(
            js_expressions=js_expr,
            key=f"_ls_clear_{int(time.time() * 1000)}",
        )
        # 改变 nonce → 下次 load 使用新 key → 强制 JS 重新执行
        st.session_state["_ls_nonce"] = int(time.time() * 1000)
    except Exception:
        pass
