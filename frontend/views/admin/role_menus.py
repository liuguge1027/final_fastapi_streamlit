import streamlit as st
import pandas as pd
from utils.api_client import api_get, api_post, api_put, api_delete
from views.admin.route_registry import register_page

# =====================================================================
# 菜单管理 (Role-Menu Mapping)
# =====================================================================

@register_page("menu:manage")
def show_menu_management():
    """菜单管理：列表展示、新增、编辑、删除角色菜单映射"""
    st.subheader("菜单管理")

    col_add, _ = st.columns([1, 5])
    with col_add:
        if st.button("➕ 新增菜单映射", key="btn_add_menu", width="stretch"):
            st.session_state.show_add_menu_dialog = True

    # 获取所有角色菜单映射
    role_menus = api_get("/role-menus/all")

    if not role_menus:
        st.info("暂无菜单映射数据")
    else:
        table_data = []
        for rm in role_menus:
            table_data.append({
                "ID": rm["id"],
                "角色编码": rm["role_code"],
                "主菜单": rm["main_menu"],
                "子菜单": rm["sub_menu"],
                "页面模块": rm.get("module_path") or "",
                "排序": rm["sort_order"],
                "创建时间": rm.get("created_at") or "",
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df, width="stretch", hide_index=True)

        # 操作区
        st.markdown("#### 操作")
        menu_options = {f"{rm['role_code']} - {rm['main_menu']} > {rm['sub_menu']} (ID: {rm['id']})": rm["id"] for rm in role_menus}
        selected_menu = st.selectbox(
            "选择菜单映射", options=list(menu_options.keys()),
            index=None, placeholder="请选择记录...", key="sel_role_menu"
        )

        if selected_menu:
            menu_id = menu_options[selected_menu]
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ 编辑", key=f"edit_menu_{menu_id}", type="primary", width="stretch"):
                    st.session_state.edit_menu_id = menu_id
                    st.session_state.show_edit_menu_dialog = True
                    st.rerun()
            with col2:
                if st.button("🗑️ 删除", key=f"del_menu_{menu_id}", width="stretch"):
                    st.session_state.delete_menu_id = menu_id
                    st.session_state.show_delete_menu_dialog = True
                    st.rerun()

    # 对话框处理
    roles = api_get("/roles") or []
    
    selected_rm_data = None
    if selected_menu:
        menu_id = menu_options[selected_menu]
        selected_rm_data = next((rm for rm in role_menus if rm["id"] == menu_id), None)

    # 弹窗触发
    if st.session_state.get("show_add_menu_dialog"):
        st.session_state.show_add_menu_dialog = False
        _add_menu_dialog(roles)
        
    if st.session_state.get("show_edit_menu_dialog"):
        st.session_state.show_edit_menu_dialog = False
        if selected_rm_data:
            _edit_menu_dialog(selected_rm_data, roles)
        else:
            st.error("无法加载编辑信息。")
            
    if st.session_state.get("show_delete_menu_dialog"):
        st.session_state.show_delete_menu_dialog = False
        if selected_rm_data:
            _delete_menu_dialog(selected_rm_data)
        else:
            st.error("无法加载删除信息。")


@st.dialog("新增菜单映射")
def _add_menu_dialog(roles):
    with st.form("add_menu_form"):
        role_codes = [r['role_code'] for r in roles]
        new_role_code = st.selectbox("角色编码 *", options=role_codes)
        new_main_menu = st.text_input("主菜单名称 *")
        new_sub_menu = st.text_input("子菜单名称 *")
        new_module_path = st.text_input("页面模块路径 (例: views.admin.pages.user_page)")
        new_sort_order = st.number_input("排序权重", value=0, step=1)
        
        submitted = st.form_submit_button("保存", type="primary")
        if submitted:
            if not new_role_code or not new_main_menu or not new_sub_menu:
                st.error("请完善必填信息！(*)")
            else:
                payload = {
                    "role_code": new_role_code,
                    "main_menu": new_main_menu,
                    "sub_menu": new_sub_menu,
                    "module_path": new_module_path,
                    "sort_order": new_sort_order
                }
                result = api_post("/role-menus", payload)
                if result:
                    st.success("添加成功！")
                    st.rerun()

@st.dialog("编辑菜单映射")
def _edit_menu_dialog(rm_data, roles):
    with st.form("edit_menu_form"):
        st.write(f"正在编辑映射 ID: **{rm_data['id']}**")
        
        role_codes = [r['role_code'] for r in roles]
        current_role_index = 0
        try:
            current_role_index = role_codes.index(rm_data['role_code'])
        except ValueError:
            pass

        edit_role_code = st.selectbox("角色编码 *", options=role_codes, index=current_role_index)
        edit_main_menu = st.text_input("主菜单名称 *", value=rm_data['main_menu'])
        edit_sub_menu = st.text_input("子菜单名称 *", value=rm_data['sub_menu'])
        edit_module_path = st.text_input("页面模块路径", value=rm_data.get('module_path') or "")
        edit_sort_order = st.number_input("排序权重", value=rm_data['sort_order'], step=1)
        
        submitted = st.form_submit_button("保存修改", type="primary")
        if submitted:
            payload = {
                "role_code": edit_role_code,
                "main_menu": edit_main_menu,
                "sub_menu": edit_sub_menu,
                "module_path": edit_module_path,
                "sort_order": edit_sort_order
            }
            result = api_put(f"/role-menus/{rm_data['id']}", payload)
            if result:
                st.success("信息已更新")
                st.rerun()

@st.dialog("删除菜单映射")
def _delete_menu_dialog(rm_data):
    st.warning(f"确定要删除映射 **{rm_data['role_code']} : {rm_data['main_menu']} > {rm_data['sub_menu']}** 吗？")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ 确认删除", type="primary", width="stretch"):
            result = api_delete(f"/role-menus/{rm_data['id']}")
            if result:
                st.success("已删除")
                st.rerun()
    with col2:
        if st.button("取消", width="stretch"):
            st.rerun()


# === show_page 包装（供统一入口调用） ===
def show_page():
    show_menu_management()
