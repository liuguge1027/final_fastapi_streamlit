"""权限管理 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.schemas.permission_schema import PermissionInfo, PermissionCreate, PermissionUpdate
from backend.services import permission_service

router = APIRouter(prefix="/permissions", tags=["权限管理"])


def _permission_to_dict(perm, include_children: bool = False) -> dict:
    """将 Permission ORM 对象转为字典，确保 children 不为 None"""
    roles = []
    if perm.roles:
        for r in perm.roles:
            roles.append({"id": r.id, "role_name": r.role_name, "role_code": r.role_code})
    children = []
    if include_children and perm.children:
        for c in perm.children:
            children.append(_permission_to_dict(c, include_children=True))
    return {
        "id": perm.id,
        "name": perm.name,
        "code": perm.code,
        "type": perm.type,
        "path": perm.path,
        "method": perm.method,
        "description": perm.description,
        "parent_id": perm.parent_id,
        "created_at": perm.created_at.isoformat() if perm.created_at else None,
        "updated_at": perm.updated_at.isoformat() if perm.updated_at else None,
        "children": children,
        "roles": roles,
    }


@router.get("")
def get_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取权限列表"""
    perms = permission_service.get_permissions(db, skip=skip, limit=limit)
    return [_permission_to_dict(p, include_children=False) for p in perms]


@router.get("/tree")
def get_permission_tree(db: Session = Depends(get_db)):
    """获取权限树结构（一次性查出，在内存中拼装以避免 N+1 查询）"""
    # 获取全部权限（这里不过滤分页获取所有）
    from backend.models.permission import Permission
    from sqlalchemy.orm import selectinload
    # 避免加载 children 以减少查询
    all_perms = db.query(Permission).options(selectinload(Permission.roles)).all()
    
    perm_dicts = []
    for p in all_perms:
        perm_dicts.append(_permission_to_dict(p, include_children=False))
        
    perm_map = {p["id"]: p for p in perm_dicts}
    tree = []
    for p in perm_dicts:
        if p["parent_id"] is None:
            tree.append(p)
        else:
            parent = perm_map.get(p["parent_id"])
            if parent:
                parent["children"].append(p)
    return tree


@router.get("/{permission_id}")
def get_permission(permission_id: int, db: Session = Depends(get_db)):
    """获取单个权限"""
    permission = permission_service.get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    return _permission_to_dict(permission)


@router.post("", response_model=PermissionInfo)
def create_permission(permission: PermissionCreate, db: Session = Depends(get_db)):
    """创建新权限"""
    existing = permission_service.get_permission_by_code(db, permission.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="权限编码已存在"
        )
    new_perm = permission_service.create_permission(db, permission)
    return _permission_to_dict(new_perm)


@router.put("/{permission_id}")
def update_permission(permission_id: int, permission_update: PermissionUpdate, db: Session = Depends(get_db)):
    """更新权限"""
    permission = permission_service.update_permission(db, permission_id, permission_update)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    return _permission_to_dict(permission)


@router.delete("/{permission_id}")
def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    """删除权限"""
    success = permission_service.delete_permission(db, permission_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    return {"message": "删除成功"}

