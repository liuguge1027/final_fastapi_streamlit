"""
API 客户端工具
==========
封装与后端 FastAPI 的 HTTP 请求
"""
import requests
import streamlit as st
from typing import Dict, Any, Optional, List

# 后端 API 基础 URL
API_BASE_URL = "http://localhost:8000"


def get_headers() -> Dict[str, str]:
    """获取请求头（包含认证 token 和客户端 IP）"""
    headers = {"Content-Type": "application/json"}
    if "access_token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    # 携带浏览器端获取的局域网 IP
    client_ip = st.session_state.get("client_ip", "")
    if client_ip:
        headers["X-Client-IP"] = client_ip
    return headers


def api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any] | List[Dict[str, Any]]]:
    """
    发送 GET 请求

    Args:
        endpoint: API 端点（不含基础 URL）
        params: 查询参数

    Returns:
        响应数据或 None（失败时）
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            headers=get_headers(),
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"请求失败: {e}")
        return None


def api_post(endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    发送 POST 请求

    Args:
        endpoint: API 端点（不含基础 URL）
        data: 请求体数据

    Returns:
        响应数据或 None（失败时）
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            headers=get_headers(),
            json=data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"请求失败: {e}")
        return None


def api_put(endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    发送 PUT 请求

    Args:
        endpoint: API 端点（不含基础 URL）
        data: 请求体数据

    Returns:
        响应数据或 None（失败时）
    """
    try:
        response = requests.put(
            f"{API_BASE_URL}{endpoint}",
            headers=get_headers(),
            json=data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"请求失败: {e}")
        return None


def api_delete(endpoint: str) -> Optional[Dict[str, Any]]:
    """
    发送 DELETE 请求

    Args:
        endpoint: API 端点（不含基础 URL）

    Returns:
        响应数据或 None（失败时）
    """
    try:
        response = requests.delete(
            f"{API_BASE_URL}{endpoint}",
            headers=get_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"请求失败: {e}")
        return None
