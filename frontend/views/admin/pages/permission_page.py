import streamlit as st
import pandas as pd
from utils.api_client import api_get, api_post, api_put, api_delete
from views.admin.route_registry import register_page

def _fetch_permissions():
    """
    安全获取权限列表。
    后端 GET /permissions 返回 PermissionInfo，包含 children 和 roles 字段。
    """
    return api_get("/permissions") or []


@register_page("permission:manage")
def show_permission_management():
    """权限管理：树形展示、新增、编辑、删除"""
    st.subheader("权限管理")

    col_add, _ = st.columns([1, 5])
    with col_add:
        if st.button("➕ 新增顶级权限", key="btn_add_top_perm", use_container_width=True):
            st.session_state.show_add_perm_dialog = True
            st.session_state.parent_id_for_new_perm = None

    perms_tree = api_get("/permissions/tree")

    if not perms_tree:
        st.info("暂无权限数据")
    else:
        st.markdown("### 权限列表")
        
        # Flatten tree for display
        flat_list = []
        def _flatten(nodes, level=0):
            for n in nodes:
                # Safely extract data treating it as a dict
                if not isinstance(n, dict):
                    continue
                flat_list.append({
                    "id": n.get("id"),
                    "展示名": "—" * level + ("▸ " if n.get("children") else "• ") + n.get("name", "Unknown"),
                    "name": n.get("name", "Unknown"),
                    "标识码": n.get("code", "N/A"),
                    "类型": "菜单" if n.get("type") == "menu" else "接口",
                    "请求路径": n.get("path") or "-",
                    "方法": n.get("method") or "-",
                    "raw_data": n
                })
                if n.get("children"):
                    _flatten(n["children"], level + 1)
                    
        _flatten(perms_tree)
        
        df = pd.DataFrame([{k: v for k, v in item.items() if k != "raw_data" and k != "name" and k != "id"} 
                          for item in flat_list])
        st.dataframe(df, use_container_width=True)

        st.markdown("#### 操作")
        perm_options = {f"{item['name']} ({item['标识码']})": item["raw_data"] for item in flat_list}
        selected_perm_key = st.selectbox("选择要操作的权限", options=list(perm_options.keys()), key="select_perm_op")
        
        selected_perm_data = perm_options.get(selected_perm_key)

        col_add_sub, col_edit, col_del, _ = st.columns([1.5, 1, 1, 3])
        if selected_perm_data:
            with col_add_sub:
                if selected_perm_data["type"] == "menu":
                    if st.button("➕ 添加子权限", key="btn_add_sub"):
                        st.session_state.parent_id_for_new_perm = selected_perm_data["id"]
                        st.session_state.parent_name_for_new_perm = selected_perm_data["name"]
                        st.session_state.show_add_perm_dialog = True
            with col_edit:
                if st.button("✏️ 编辑", key="btn_edit_perm"):
                    st.session_state.show_edit_perm_dialog = True
            with col_del:
                if st.button("🗑️ 删除", key="btn_del_perm"):
                    st.session_state.show_delete_perm_dialog = True

    st.divider()

    # 弹窗处理
    if st.session_state.get("show_add_perm_dialog"):
        st.session_state.show_add_perm_dialog = False
        _add_perm_dialog(st.session_state.get("parent_id_for_new_perm"), st.session_state.get("parent_name_for_new_perm"))
        
    if st.session_state.get("show_edit_perm_dialog"):
        st.session_state.show_edit_perm_dialog = False
        if selected_perm_data:
            _edit_perm_dialog(selected_perm_data)
        else:
            st.error("无法加载权限编辑信息。")
            
    if st.session_state.get("show_delete_perm_dialog"):
        st.session_state.show_delete_perm_dialog = False
        if selected_perm_data:
            _delete_perm_dialog(selected_perm_data)
        else:
            st.error("无法加载权限删除信息。")


@st.dialog("新增权限")
def _add_perm_dialog(parent_id, parent_name=None):
    with st.form("add_perm_form"):
        if parent_id:
            st.info(f"正在为【{parent_name}】添加子权限")
        else:
            st.info("正在添加顶级权限 (通常是菜单)")

        perm_name = st.text_input("权限名称 *", placeholder="如: 用户管理")
        perm_code = st.text_input("权限标识 *", placeholder="如: user:manage")
        perm_type = st.radio("类型", options=["menu", "api"], format_func=lambda x: "菜单 (menu)" if x == "menu" else "接口 (api)", horizontal=True)
        path = st.text_input("路径 / URL", placeholder="如: /users (菜单路径或API路径)")
        method = st.selectbox("API 方法 (仅接口需填)", options=["", "GET", "POST", "PUT", "DELETE"])
        description = st.text_area("描述")

        submitted = st.form_submit_button("保存", type="primary")
        if submitted:
            if not perm_name or not perm_code:
                st.error("权限名称和标识为必填项！")
            else:
                perm_data = {
                    "name": perm_name,
                    "code": perm_code,
                    "type": perm_type,
                    "parent_id": parent_id,
                    "path": path if path else None,
                    "method": method if (perm_type == "api" and method) else None,
                    "description": description if description else None,
                }
                result = api_post("/permissions", perm_data)
                if result:
                    st.success("权限创建成功！")
                    st.session_state.show_add_perm_dialog = False
                    st.rerun()

@st.dialog("编辑权限")
def _edit_perm_dialog(perm_data):
    with st.form("edit_perm_form"):
        st.write(f"正在编辑权限：**{perm_data['name']}**")
        
        perm_name = st.text_input("权限名称 *", value=perm_data.get("name", ""))
        perm_code = st.text_input("权限标识 *", value=perm_data.get("code", ""))
        
        type_idx = 0 if perm_data.get("type", "menu") == "menu" else 1
        perm_type = st.radio("类型", options=["menu", "api"], index=type_idx, format_func=lambda x: "菜单 (menu)" if x == "menu" else "接口 (api)", horizontal=True)
        
        path = st.text_input("路径 / URL", value=perm_data.get("path") or "")
        
        method_opts = ["", "GET", "POST", "PUT", "DELETE"]
        current_method = perm_data.get("method") or ""
        method_idx = method_opts.index(current_method) if current_method in method_opts else 0
        method = st.selectbox("API 方法", options=method_opts, index=method_idx)
        
        description = st.text_area("描述", value=perm_data.get("description") or "")

        submitted = st.form_submit_button("保存", type="primary")
        if submitted:
            if not perm_name or not perm_code:
                st.error("权限名称和标识为必填项！")
            else:
                update_data = {
                    "name": perm_name,
                    "code": perm_code,
                    "type": perm_type,
                    "path": path if path else None,
                    "method": method if (perm_type == "api" and method) else None,
                    "description": description if description else None,
                }
                result = api_put(f"/permissions/{perm_data['id']}", update_data)
                if result:
                    st.success("权限更新成功！")
                    st.session_state.show_edit_perm_dialog = False
                    st.rerun()

@st.dialog("删除权限")
def _delete_perm_dialog(perm_data):
    if perm_data.get("children"):
        st.error(f"该权限 (**{perm_data['name']}**) 包含子节点，请先删除子节点！")
        if st.button("关闭"):
            st.session_state.show_delete_perm_dialog = False
            st.rerun()
        return

    st.warning(f"确定要删除权限 **{perm_data['name']}** 吗？此操作不可撤销！")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("确认删除", type="primary", use_container_width=True):
            result = api_delete(f"/permissions/{perm_data['id']}")
            if result:
                st.success("删除成功！")
                st.session_state.show_delete_perm_dialog = False
                st.rerun()
    with col2:
        if st.button("取消", use_container_width=True):
            st.session_state.show_delete_perm_dialog = False
            st.rerun()


# === show_page 包装（供统一入口调用） ===
def show_page():
    show_permission_management()

