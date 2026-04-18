"""
员工可视化看板页面
================
展示员工统计数据、部门分布、入职趋势及详细列表。
"""
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from utils.api_client import api_get

def load_data():
    """从后端获取用户数据并转换为 DataFrame"""
    users = api_get("/users")
    if not users:
        return pd.DataFrame()
    
    df = pd.DataFrame(users)
    # 格式化日期
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['join_month'] = df['created_at'].dt.strftime('%Y-%m')
    
    # 数据增强：将角色映射为具体的业务部门（发散思维）
    role_dept_map = {
        "ADMIN": "管理中心",
        "SALE": "营销部",
        "HR": "人力资源部",
        "FINANCE": "财务部",
        "USER": "研发中心"
    }
    df['department'] = df['role_code'].map(role_dept_map).fillna("通用部")
    
    # 状态转换
    df['status'] = df['is_active'].apply(lambda x: "🟢 活跃" if x == 1 else "🔴 禁用")
    
    return df

def show_page():
    st.title("👥 员工管理看板")
    st.markdown("---")

    # 1. 加载数据
    with st.spinner("正在加载员工数据..."):
        df = load_data()

    if df.empty:
        st.warning("⚠️ 暂无员工数据，请先创建用户。")
        if st.button("🔄 刷新"):
            st.rerun()
        return

    # 2. 侧边栏筛选
    st.sidebar.header("🔍 数据筛选")
    all_depts = ["全部"] + sorted(df['department'].unique().tolist())
    selected_dept = st.sidebar.selectbox("所属部门", all_depts)
    
    all_statuses = ["全部"] + sorted(df['status'].unique().tolist())
    selected_status = st.sidebar.selectbox("账号状态", all_statuses)
    
    search_query = st.sidebar.text_input("搜索姓名或邮箱", "").lower()

    # 应用筛选逻辑
    filtered_df = df.copy()
    if selected_dept != "全部":
        filtered_df = filtered_df[filtered_df['department'] == selected_dept]
    if selected_status != "全部":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if search_query:
        filtered_df = filtered_df[
            filtered_df['username'].str.lower().contains(search_query) | 
            filtered_df['email'].str.lower().contains(search_query)
        ]

    # 3. 核心指标 KPI
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    total_count = len(df)
    active_count = len(df[df['is_active'] == 1])
    recent_count = len(df[df['created_at'] > (datetime.now() - timedelta(days=30))])
    dept_count = df['department'].nunique()

    kpi_col1.metric("员工总数", f"{total_count} 人", help="系统中注册的总用户数")
    kpi_col2.metric("活跃员工", f"{active_count} 人", f"{active_count/total_count:.1%}", delta_color="normal")
    kpi_col3.metric("本月新入职", f"{recent_count} 人", f"+{recent_count}", delta_color="normal")
    kpi_col4.metric("覆盖部门", f"{dept_count} 个")

    st.markdown("### 📊 维度统计")
    
    # 4. 可视化图表
    chart_row1_col1, chart_row1_col2 = st.columns(2)

    with chart_row1_col1:
        st.subheader("🏢 部门人数分布")
        dept_dist = filtered_df.groupby('department').size().reset_index(name='人数')
        base_chart = alt.Chart(dept_dist).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X('department:N', title='部门', sort='-y'),
            y=alt.Y('人数:Q', title='员工数量'),
            color=alt.Color('department:N', legend=None, scale=alt.Scale(scheme='tableau10')),
            tooltip=['department', '人数']
        ).properties(height=300)
        st.altair_chart(base_chart, width="stretch")

    with chart_row1_col2:
        st.subheader("⚖️ 账号状态比例")
        status_dist = filtered_df.groupby('status').size().reset_index(name='count')
        pie_chart = alt.Chart(status_dist).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="count", type="quantitative"),
            color=alt.Color(field="status", type="nominal", scale=alt.Scale(range=['#2ecc71', '#e74c3c'])),
            tooltip=['status', 'count']
        ).properties(height=300)
        st.altair_chart(pie_chart, width="stretch")

    st.markdown("### 📈 入职趋势 (累计)")
    # 计算累计增长
    trend_df = df.copy().sort_values('created_at')
    trend_df['count'] = 1
    trend_df['cumulative_count'] = trend_df['count'].cumsum()
    
    area_chart = alt.Chart(trend_df).mark_area(
        line={'color': 'darkblue'},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='white', offset=0),
                   alt.GradientStop(color='darkblue', offset=1)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X('created_at:T', title='时间'),
        y=alt.Y('cumulative_count:Q', title='累计员工人数'),
        tooltip=[alt.Tooltip('created_at:T', title='日期'), alt.Tooltip('cumulative_count:Q', title='总人数')]
    ).properties(height=250)
    st.altair_chart(area_chart, width="stretch")

    # 5. 详细列表
    st.markdown("### 📋 员工详情列表")
    display_cols = [
        "username", "email", "department", "role_name", "status", "created_at"
    ]
    # 对前端展示列进行重命名
    rename_dict = {
        "username": "姓名/用户名",
        "email": "电子邮箱",
        "department": "所属部门",
        "role_name": "系统角色",
        "status": "状态",
        "created_at": "入职时间"
    }
    
    styled_df = filtered_df[display_cols].rename(columns=rename_dict)
    
    # 使用 st.dataframe 展示，增加搜索和筛选能力
    st.dataframe(
        styled_df,
        width="stretch",
        hide_index=True,
        column_config={
            "入职时间": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm"),
            "电子邮箱": st.column_config.LinkColumn()
        }
    )

    if st.button("🔄 刷新数据"):
        st.rerun()

