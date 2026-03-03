import functools

ROUTE_MAP = {}

def register_page(code: str):
    """
    路由装饰器：将菜单的 code 绑定到特定的渲染函数。
    用法:
        @register_page("user:manage")
        def show_user_management():
            ...
    """
    def decorator(func):
        ROUTE_MAP[code] = func
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
