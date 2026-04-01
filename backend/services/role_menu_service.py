from sqlalchemy.orm import Session
from backend.models.role_menu import RoleMenu

def get_role_menus(db: Session, skip: int = 0, limit: int = 100):
    """获取所有角色菜单映射（不分组）"""
    return db.query(RoleMenu).offset(skip).limit(limit).all()

def get_role_menu_by_id(db: Session, menu_id: int):
    """根据 ID 获取单个映射"""
    return db.query(RoleMenu).filter(RoleMenu.id == menu_id).first()

def create_role_menu(db: Session, role_code: str, main_menu: str, sub_menu: str, module_path: str = None, sort_order: int = 0):
    """创建新的角色菜单映射"""
    db_menu = RoleMenu(
        role_code=role_code,
        main_menu=main_menu,
        sub_menu=sub_menu,
        module_path=module_path,
        sort_order=sort_order
    )
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu

def update_role_menu(db: Session, menu_id: int, **kwargs):
    """更新角色菜单映射"""
    db_menu = get_role_menu_by_id(db, menu_id)
    if not db_menu:
        return None
    
    for key, value in kwargs.items():
        if hasattr(db_menu, key):
            setattr(db_menu, key, value)
            
    db.commit()
    db.refresh(db_menu)
    return db_menu

def delete_role_menu(db: Session, menu_id: int):
    """删除角色菜单映射"""
    db_menu = get_role_menu_by_id(db, menu_id)
    if not db_menu:
        return False
    
    db.delete(db_menu)
    db.commit()
    return True
