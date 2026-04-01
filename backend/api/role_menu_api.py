from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.models.role_menu import RoleMenu
from backend.schemas.role_menu_schema import RoleMenu as RoleMenuSchema, RoleMenuCreate, RoleMenuUpdate
from backend.services import role_menu_service
from backend.core.auth import get_current_user, require_permission

router = APIRouter(
    prefix="/role-menus",
    tags=["角色菜单"],
    dependencies=[Depends(get_current_user)]
)

@router.get("")
def get_all_role_menus(db: Session = Depends(get_db)):
    """获取所有角色的菜单配置（侧边栏专用格式）"""
    menus = db.query(RoleMenu).order_by(RoleMenu.sort_order).all()
    
    result = {}
    for menu in menus:
        # 兼容原有的小写 role_code 格式
        role = menu.role_code.lower()
        if role not in result:
            result[role] = {}
        
        if menu.main_menu not in result[role]:
            result[role][menu.main_menu] = []
            
        result[role][menu.main_menu].append({
            "sub_menu": menu.sub_menu,
            "module_path": menu.module_path
        })
        
    return result

@router.get("/all", response_model=List[RoleMenuSchema])
def get_role_menus_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有角色菜单映射（管理列表专用）"""
    return role_menu_service.get_role_menus(db, skip=skip, limit=limit)

@router.post("", response_model=RoleMenuSchema,
             dependencies=[Depends(require_permission("menu:create"))])
def create_role_menu(menu: RoleMenuCreate, db: Session = Depends(get_db)):
    """创建新的角色菜单映射（需要 menu:create 权限）"""
    return role_menu_service.create_role_menu(
        db, 
        role_code=menu.role_code,
        main_menu=menu.main_menu,
        sub_menu=menu.sub_menu,
        module_path=menu.module_path,
        sort_order=menu.sort_order
    )

@router.put("/{menu_id}", response_model=RoleMenuSchema,
            dependencies=[Depends(require_permission("menu:update"))])
def update_role_menu(menu_id: int, menu_update: RoleMenuUpdate, db: Session = Depends(get_db)):
    """更新角色菜单映射（需要 menu:update 权限）"""
    menu = role_menu_service.update_role_menu(db, menu_id, **menu_update.dict(exclude_unset=True))
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单映射不存在"
        )
    return menu

@router.delete("/{menu_id}",
               dependencies=[Depends(require_permission("menu:delete"))])
def delete_role_menu(menu_id: int, db: Session = Depends(get_db)):
    """删除角色菜单映射（需要 menu:delete 权限）"""
    success = role_menu_service.delete_role_menu(db, menu_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单映射不存在"
        )
    return {"message": "删除成功"}
