import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.api_client import api_get, api_delete
from views.admin.route_registry import register_page


# ── 批量删除确认对话框 ──

@st.dialog("确认删除 7 天前日志")
def confirm_cleanup_7days():
    st.warning("⚠️ 此操作将删除 **7 天前** 的所有操作日志，不可恢复！")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("确认删除", key="confirm_del_7d", type="primary", width="stretch"):
            result = api_delete("/operation-logs/cleanup?days=7")
            if result is not None:
                st.success("删除成功！")
                st.rerun()
            else:
                st.error("删除失败，请检查后端日志")
    with c2:
        if st.button("取消", key="cancel_del_7d", width="stretch"):
            st.rerun()


@st.dialog("确认删除 30 天前日志")
def confirm_cleanup_30days():
    st.warning("⚠️ 此操作将删除 **30 天前** 的所有操作日志，不可恢复！")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("确认删除", key="confirm_del_30d", type="primary", width="stretch"):
            result = api_delete("/operation-logs/cleanup?days=30")
            if result is not None:
                st.success("删除成功！")
                st.rerun()
            else:
                st.error("删除失败，请检查后端日志")
    with c2:
        if st.button("取消", key="cancel_del_30d", width="stretch"):
            st.rerun()


@st.dialog("确认删除昨天的日志")
def confirm_cleanup_yesterday():
    st.warning("⚠️ 此操作将删除 **昨天** 的所有操作日志，不可恢复！")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("确认删除", key="confirm_del_1d", type="primary", width="stretch"):
            result = api_delete("/operation-logs/cleanup?days=1")
            if result is not None:
                st.success("删除成功！")
                st.rerun()
            else:
                st.error("删除失败，请检查后端日志")
    with c2:
        if st.button("取消", key="cancel_del_1d", width="stretch"):
            st.rerun()


@register_page("log:manage")
def show_operation_log_management():
    """操作日志管理：列表展示、按用户过滤、按时间过滤、批量删除"""
    st.subheader("操作日志管理")

    # ── 批量删除按钮 ──
    del_col1, del_col2, del_col3, del_spacer = st.columns([1, 1, 1, 3])
    with del_col1:
        if st.button("🗑 删除 7 天前", key="btn_cleanup_7d", width="stretch"):
            confirm_cleanup_7days()
    with del_col2:
        if st.button("🗑 删除 30 天前", key="btn_cleanup_30d", width="stretch"):
            confirm_cleanup_30days()
    with del_col3:
        if st.button("🗑 删除昨天", key="btn_cleanup_1d", width="stretch"):
            confirm_cleanup_yesterday()

    st.divider()

    # ── 过滤条件 ──
    col_user, col_start, col_end, col_search = st.columns([2, 2, 2, 1])

    with col_user:
        users = api_get("/users") or []
        user_filter_options = {"全部用户": None}
        user_filter_options.update({u["username"]: u["id"] for u in users})
        selected_user_filter = st.selectbox(
            "按用户过滤", options=list(user_filter_options.keys()), key="log_user_filter"
        )

    with col_start:
        start_date = st.date_input(
            "开始日期",
            value=datetime.now().date() - timedelta(days=30),
            key="log_start_date"
        )

    with col_end:
        end_date = st.date_input(
            "结束日期",
            value=datetime.now().date(),
            key="log_end_date"
        )

    with col_search:
        st.markdown("<br>", unsafe_allow_html=True)
        do_search = st.button("🔍 查询", key="btn_search_log", width="stretch")

    # 构建查询参数
    params = {}
    user_id_filter = user_filter_options.get(selected_user_filter)
    if user_id_filter:
        params["user_id"] = user_id_filter
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()

    logs = api_get("/operation-logs", params=params)

    if not logs:
        st.info("暂无操作日志")
        return

    table_data = []
    for log in logs:
        user_info = log.get("user")
        username = user_info["username"] if user_info else "系统"

        table_data.append({
            "ID": log["id"],
            "操作用户": username,
            "操作名称": log.get("action") or "",
            "HTTP 方法": log.get("method") or "",
            "请求路径": log.get("path") or "",
            "状态码": log.get("status_code") or "",
            "结果": "成功" if log.get("success") == 1 else "失败",
            "IP": log.get("ip") or "",
            "耗时(ms)": log.get("latency_ms") or "",
            "时间": log.get("created_at") or "",
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, width="stretch", hide_index=True)

    st.caption(f"共 {len(logs)} 条记录")


# === show_page 包装（供统一入口调用） ===
def show_page():
    show_operation_log_management()

