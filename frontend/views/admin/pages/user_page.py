import streamlit as st
import pandas as pd
from utils.api_client import api_get, api_post, api_put, api_delete
from views.admin.route_registry import register_page

# =====================================================================
# 用户管理
# =====================================================================

@register_page("user:manage")
def show_user_management():
    """用户管理：列表展示、新增、编辑、删除"""
    st.subheader("用户管理")

    col_add, _ = st.columns([1, 5])
    with col_add:
        if st.button("➕ 新增用户", key="btn_add_user", use_container_width=True):
            st.session_state.show_add_user_dialog = True

    users = api_get("/users")

    if not users:
        st.info("暂无用户数据")
    else:
        table_data = []
        for user in users:
            table_data.append({
                "ID": user["id"],
                "用户名": user["username"],
                "邮箱": user.get("email") or "",
                "角色": user.get("role_name") or "",
                "状态": "启用" if user.get("is_active") == 1 else "禁用",
                "超级管理员": "是" if user.get("is_superuser") == 1 else "否",
                "最后登录": user.get("last_login") or "从未登录",
                "创建时间": user.get("created_at") or "",
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 操作区
        st.markdown("#### 操作")
        user_options = {f"{u['username']} (ID: {u['id']})": u["id"] for u in users}
        selected_user = st.selectbox(
            "选择用户", options=list(user_options.keys()),
            index=None, placeholder="请选择用户...", key="sel_user"
        )

        if selected_user:
            user_id = user_options[selected_user]
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ 编辑", key=f"edit_user_{user_id}", type="primary", use_container_width=True):
                    st.session_state.edit_user_id = user_id
                    st.session_state.show_edit_user_dialog = True
                    st.rerun()
            with col2:
                if st.button("🗑️ 删除", key=f"del_user_{user_id}", use_container_width=True):
                    st.session_state.delete_user_id = user_id
                    st.session_state.show_delete_user_dialog = True
                    st.rerun()

    # 对话框处理
    roles = api_get("/roles") or []
    
    selected_user_data = None
    if selected_user:
        user_id = user_options[selected_user]
        selected_user_data = next((u for u in users if u["id"] == user_id), None)

    # 弹窗触发
    if st.session_state.get("show_add_user_dialog"):
        st.session_state.show_add_user_dialog = False
        _add_user_dialog(roles)
        
    if st.session_state.get("show_edit_user_dialog"):
        st.session_state.show_edit_user_dialog = False
        if selected_user_data:
            _edit_user_dialog(selected_user_data, roles)
        else:
            st.error("无法加载用户编辑信息。")
            
    if st.session_state.get("show_delete_user_dialog"):
        st.session_state.show_delete_user_dialog = False
        if selected_user_data:
            _delete_user_dialog(selected_user_data)
        else:
            st.error("无法加载用户删除信息。")


@st.dialog("新增用户")
def _add_user_dialog(roles):
    with st.form("add_user_form"):
        new_username = st.text_input("用户名 *")
        new_password = st.text_input("密码 *", type="password")
        new_email = st.text_input("邮箱")
        
        role_options_dict = {f"{r['role_name']} (ID: {r['id']})": r["id"] for r in roles}
        new_role_val = st.selectbox("分配角色 *", options=list(role_options_dict.keys()))
        
        is_superuser = st.checkbox("设为超级管理员")
        is_active = st.checkbox("启用账户", value=True)
        
        submitted = st.form_submit_button("保存", type="primary")
        if submitted:
            if not new_username or not new_password or not new_role_val:
                st.error("请完善必填信息！(*)")
            else:
                new_user_data = {
                    "username": new_username,
                    "password": new_password,
                    "email": new_email,
                    "role_id": role_options_dict[new_role_val],
                    "is_superuser": 1 if is_superuser else 0,
                    "is_active": 1 if is_active else 0
                }
                result = api_post("/users", new_user_data)
                if result:
                    st.success("用户添加成功！")
                    st.session_state.show_add_user_dialog = False # Close dialog
                    st.rerun()

@st.dialog("编辑用户")
def _edit_user_dialog(user_data, roles):
    with st.form("edit_user_form"):
        st.write(f"正在编辑用户：**{user_data['username']}** (ID: {user_data['id']})")
        
        edit_email = st.text_input("邮箱", value=user_data.get("email") or "")
        
        role_options_dict = {f"{r['role_name']} (ID: {r['id']})": r["id"] for r in roles}
        
        # 找到当前角色的 index
        current_role_id = user_data.get("role_id")
        current_index = 0
        if current_role_id:
            for i, option_str in enumerate(role_options_dict.keys()):
                if role_options_dict[option_str] == current_role_id:
                    current_index = i
                    break

        edit_role_val = st.selectbox("修改角色 *", options=list(role_options_dict.keys()), index=current_index)
        
        is_su = st.checkbox("超级管理员", value=bool(user_data.get("is_superuser")))
        is_act = st.checkbox("启用账户", value=bool(user_data.get("is_active")))
        
        # 密码可选修改
        edit_password = st.text_input("新密码 (留空则不修改)", type="password")
        
        submitted = st.form_submit_button("保存修改", type="primary")
        if submitted:
            update_data = {
                "email": edit_email,
                "role_id": role_options_dict[edit_role_val],
                "is_superuser": 1 if is_su else 0,
                "is_active": 1 if is_act else 0
            }
            if edit_password:
                update_data["password"] = edit_password
                
            result = api_put(f"/users/{user_data['id']}", update_data)
            if result:
                st.success("用户信息已更新")
                st.session_state.show_edit_user_dialog = False # Close dialog
                st.rerun()

@st.dialog("删除用户")
def _delete_user_dialog(user_data):
    st.warning(f"确定要删除用户 **{user_data['username']}** 吗？此操作不可恢复。")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ 确认删除", type="primary", use_container_width=True):
            result = api_delete(f"/users/{user_data['id']}")
            if result:
                st.success("用户已删除")
                st.session_state.show_delete_user_dialog = False # Close dialog
                st.rerun()
    with col2:
        if st.button("取消", use_container_width=True):
            st.session_state.show_delete_user_dialog = False # Close dialog
            st.rerun()


# === show_page 包装（供统一入口调用） ===
def show_page():
    show_user_management()

