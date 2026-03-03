import streamlit as st
import pandas as pd
from utils.api_client import api_get, api_post
from views.admin.route_registry import register_page

# 如果你需要此函数可以自行导入，本文件里展示逻辑并未使用它
from views.admin.pages.permission_page import _fetch_permissions

@register_page("role_permission:manage")
def show_role_permission_management():
    """角色权限管理：查看角色已有权限、分配权限、移除权限"""
    st.subheader("角色权限管理")

    roles = api_get("/roles")
    if not roles:
        st.info("暂无角色数据，请先创建角色")
        return

    role_options = {f"{r['role_name']} (ID: {r['id']})": r["id"] for r in roles}
    selected_role = st.selectbox(
        "选择角色", options=list(role_options.keys()),
        index=None, placeholder="请选择角色...", key="sel_role_perm"
    )

    if not selected_role:
        st.info("请先选择一个角色查看其权限")
        return

    role_id = role_options[selected_role]

    # 直接通过 API 获取角色已分配的权限
    role_permissions = api_get(f"/roles/{role_id}/permissions") or []
    all_permissions = _fetch_permissions()

    # 展示当前权限
    st.markdown("#### 当前已分配权限")
    if role_permissions:
        table_data = []
        for rp in role_permissions:
            table_data.append({
                "权限ID": rp["id"],
                "权限名称": rp["name"],
                "权限编码": rp["code"],
                "类型": rp.get("type") or "",
                "描述": rp.get("description") or "",
            })
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("该角色暂无任何权限")

    st.divider()

    # 分配权限（多选）
    st.markdown("#### 分配权限")
    assigned_ids = {p["id"] for p in role_permissions}
    available_perms = [p for p in all_permissions if p["id"] not in assigned_ids]

    all_perms = api_get("/permissions/tree")

    if not roles or not all_perms:
        st.info("请先确保系统中有角色和权限数据")
        return

    role_options = {f"{r['role_name']} ({r['role_code']})": r["id"] for r in roles}
    selected_role_key = st.selectbox("选择要配置的角色", options=list(role_options.keys()))
    
    selected_role_id = role_options[selected_role_key]

    # 获取该角色当前已分配的权限
    current_role_perms = api_get(f"/roles/{selected_role_id}/permissions") or []
    current_perm_ids = [p["id"] for p in current_role_perms]

    st.markdown(f"#### 配置【{selected_role_key}】的权限")
    
    # 递归生成复选框树
    def _render_perm_checkboxes(nodes, level=0):
        selected_ids = []
        for node in nodes:
            indent = "---" * level
            col1, col2 = st.columns([1, 10])
            with col1:
                st.write("") # placeholder
            with col2:
                # 使用 st.checkbox，通过 key 区分
                is_checked = st.checkbox(
                    f"{indent} {node['name']} ({node['code']})", 
                    value=node["id"] in current_perm_ids,
                    key=f"chk_perm_{selected_role_id}_{node['id']}"
                )
                if is_checked:
                    selected_ids.append(node["id"])
            
            if node.get("children"):
                selected_ids.extend(_render_perm_checkboxes(node["children"], level + 1))
        return selected_ids

    with st.form(key=f"form_role_perm_{selected_role_id}"):
        st.caption("勾选对应的权限节点，未勾选即表示移除。")
        new_selected_ids = _render_perm_checkboxes(all_perms)
        
        submitted = st.form_submit_button("保存权限配置", type="primary")
        if submitted:
            # 新增的权限
            perms_to_add = list(set(new_selected_ids) - set(current_perm_ids))
            # 需要移除的权限
            perms_to_remove = list(set(current_perm_ids) - set(new_selected_ids))
            
            success = True
            if perms_to_add:
                res_add = api_post(f"/roles/{selected_role_id}/permissions", {"permission_ids": perms_to_add})
                if not res_add: success = False
                
            if perms_to_remove:
                # 因 frontend api_delete 可能不支持传 body，根据你的后端实现，通常可能是类似 POST /remove 或者直接在 PUT 里全量更新
                # 这里假设你的后端 /roles/{id}/permissions/remove 支持
                res_remove = api_post(f"/roles/{selected_role_id}/permissions/remove", {"permission_ids": perms_to_remove})
                if not res_remove: success = False
                
            if success:
                st.success("角色权限配置成功！")
                st.rerun()
            else:
                st.error("部分权限配置失败，请检查网络或后端日志。")


# === show_page 包装（供统一入口调用） ===
def show_page():
    show_role_permission_management()

