import streamlit as st
import pandas as pd
from utils.api_client import api_get, api_post, api_put, api_delete
from views.admin.route_registry import register_page

# =====================================================================
# 角色管理
# =====================================================================

@register_page("role:manage")
def show_role_management():
    """角色管理：列表展示、新增、编辑、删除"""
    st.subheader("角色管理")

    col_add, _ = st.columns([1, 5])
    with col_add:
        if st.button("➕ 新增角色", key="btn_add_role", width="stretch"):
            st.session_state.show_add_role_dialog = True

    roles = api_get("/roles")

    if not roles:
        st.info("暂无角色数据")
    else:
        table_data = []
        for role in roles:
            table_data.append({
                "ID": role["id"],
                "角色名称": role["role_name"],
                "角色编码": role["role_code"],
                "描述": role.get("description") or "",
                "创建时间": role.get("created_at") or "",
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, width="stretch", hide_index=True)

        # 操作区
        st.markdown("#### 操作")
        role_options = {f"{r['role_name']} ({r['role_code']})": r["id"] for r in roles}
        selected_role = st.selectbox("选择要操作的角色", options=list(role_options.keys()), key="select_role_op")

        col_edit, col_del, _ = st.columns([1, 1, 4])
        with col_edit:
            if st.button("✏️ 编辑", key="btn_edit_role"):
                st.session_state.show_edit_role_dialog = True
        with col_del:
            if st.button("🗑️ 删除", key="btn_del_role"):
                st.session_state.show_delete_role_dialog = True

    st.divider()

    selected_role_data = None
    if selected_role:
        role_id = role_options[selected_role]
        selected_role_data = next((r for r in roles if r["id"] == role_id), None)

    # 弹窗触发
    if st.session_state.get("show_add_role_dialog"):
        st.session_state.show_add_role_dialog = False
        _add_role_dialog()
        
    if st.session_state.get("show_edit_role_dialog"):
        st.session_state.show_edit_role_dialog = False
        if selected_role_data:
            _edit_role_dialog(selected_role_data)
        else:
            st.error("无法加载角色编辑信息。")
            
    if st.session_state.get("show_delete_role_dialog"):
        st.session_state.show_delete_role_dialog = False
        if selected_role_data:
            _delete_role_dialog(selected_role_data)
        else:
            st.error("无法加载角色删除信息。")


@st.dialog("新增角色")
def _add_role_dialog():
    with st.form("add_role_form"):
        role_name = st.text_input("角色名称 *", placeholder="如：管理员")
        role_code = st.text_input("角色编码 *", placeholder="如：ADMIN")
        description = st.text_area("角色描述", placeholder="描述该角色的权限范围")

        submitted = st.form_submit_button("创建", type="primary")
        if submitted:
            if not role_name or not role_code:
                st.error("角色名称和编码为必填项！")
            else:
                role_data = {
                    "role_name": role_name,
                    "role_code": role_code.upper(),
                    "description": description if description else None,
                }
                result = api_post("/roles", role_data)
                if result:
                    st.success("角色创建成功！")
                    st.session_state.show_add_role_dialog = False
                    st.rerun()

@st.dialog("编辑角色")
def _edit_role_dialog(role_data):
    with st.form("edit_role_form"):
        st.write(f"正在编辑角色：**{role_data['role_name']}**")
        
        role_name = st.text_input("角色名称 *", value=role_data.get("role_name", ""))
        role_code = st.text_input("角色编码 *", value=role_data.get("role_code", ""))
        description = st.text_area("角色描述", value=role_data.get("description", ""))

        submitted = st.form_submit_button("保存", type="primary")
        if submitted:
            if not role_name or not role_code:
                st.error("角色名称和编码为必填项！")
            else:
                update_data = {
                    "role_name": role_name,
                    "role_code": role_code.upper(),
                    "description": description if description else None,
                }
                result = api_put(f"/roles/{role_data['id']}", update_data)
                if result:
                    st.success("角色更新成功！")
                    st.session_state.show_edit_role_dialog = False
                    st.rerun()

@st.dialog("删除角色")
def _delete_role_dialog(role_data):
    st.warning(f"确定要删除角色 **{role_data['role_name']}** 吗？此操作不可撤销！")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("确认删除", type="primary", width="stretch"):
            result = api_delete(f"/roles/{role_data['id']}")
            if result:
                st.success("删除成功！")
                st.session_state.show_delete_role_dialog = False
                st.rerun()
    with col2:
        if st.button("取消", width="stretch"):
            st.session_state.show_delete_role_dialog = False
            st.rerun()


# === show_page 包装（供统一入口调用） ===
def show_page():
    show_role_management()

