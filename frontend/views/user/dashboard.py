"""
用户仪表盘
========
USER 角色的仪表盘页面
"""
import streamlit as st
import pandas as pd
import numpy as np


def show_page():
    """显示用户仪表盘"""
    st.title("📊 个人仪表盘")
    st.divider()

    # 欢迎信息
    st.success(f"欢迎，{st.session_state.get('username', '用户')}！这是您的个人工作台。")

    st.divider()

    # 示例统计卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("待办任务", "5", "+2")
    with col2:
        st.metric("本周完成", "12", "0")
    with col3:
        st.metric("本月完成", "45", "+8")
    with col4:
        st.metric("团队排名", "3", "-1")

    st.divider()

    # 示例图表
    st.subheader("工作趋势")

    # 生成示例数据
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=["任务量", "完成率", "效率"]
    )

    st.line_chart(chart_data)

    st.divider()

    # 最近活动
    st.subheader("最近活动")
    activities = [
        {"时间": "10:30", "活动": "完成了任务 A"},
        {"时间": "09:15", "活动": "提交了报告"},
        {"时间": "昨天", "活动": "参加了团队会议"},
        {"时间": "昨天", "活动": "更新了个人资料"}
    ]

    for activity in activities:
        st.text(f"⏰ {activity['时间']} - {activity['活动']}")
