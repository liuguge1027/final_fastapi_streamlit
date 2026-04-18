import re
import time
import json
import jwt

from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.db.database import Base, engine, SessionLocal
from backend.models.user import User  # noqa: F401
from backend.models.role import Role  # noqa: F401
from backend.models.operation_log import OperationLog  # noqa: F401
from backend.models.role_menu import RoleMenu  # noqa: F401

from backend.api.auth import router as auth_router
from backend.api.user_api import router as user_router
from backend.api.role_api import router as role_router
from backend.api.operation_log_api import router as operation_log_router
from backend.api.role_menu_api import router as role_menu_router

from backend.core.security import SECRET_KEY, ALGORITHM
from backend.services.user_service import get_user_by_username
from backend.services import operation_log_service


# ──────────────────────────────────────────────
#  操作日志匹配规则（硬编码，替代原 permissions 表）
# ──────────────────────────────────────────────

# whitelist_ips = ["127.0.0.1","192.168.1.2"]
whitelist_ips = []

# 操作日志规则：(HTTP方法, URL路径模板, 操作名称)
# 路径模板中的 {xxx} 会被转为正则 [^/]+
_OPERATION_LOG_RULES_RAW = [
    # 用户管理
    ("POST",   "/users",           "创建用户"),
    ("PUT",    "/users/{id}",      "编辑用户"),
    ("DELETE", "/users/{id}",      "删除用户"),
    # 角色管理
    ("POST",   "/roles",           "创建角色"),
    ("PUT",    "/roles/{id}",      "编辑角色"),
    ("DELETE", "/roles/{id}",      "删除角色"),
    # 菜单管理
    ("POST",   "/role-menus",      "创建菜单映射"),
    ("PUT",    "/role-menus/{id}", "编辑菜单映射"),
    ("DELETE", "/role-menus/{id}", "删除菜单映射"),
    # 操作日志
    ("DELETE", "/operation-logs/cleanup", "清理操作日志"),
    # 认证
    ("POST",   "/auth/login",      "用户登录"),
]


def _path_to_regex(path_template: str) -> re.Pattern:
    """
    将路径模板转为正则:
      /users/{id}             →  ^/users/[^/]+$
      /roles/{id}/permissions →  ^/roles/[^/]+/permissions$
    """
    pattern = re.sub(r"\{[^}]+\}", r"[^/]+", path_template)
    return re.compile(f"^{pattern}$")


# 编译后的规则缓存：[(method, compiled_regex, action_name), ...]
_operation_log_rules: list[tuple[str, re.Pattern, str]] = []


def _compile_log_rules():
    """编译操作日志匹配规则"""
    global _operation_log_rules
    rules = []
    for method, path, name in _OPERATION_LOG_RULES_RAW:
        regex = _path_to_regex(path)
        rules.append((method.upper(), regex, name))
    # 按路径长度降序排列，优先匹配更具体的路径
    rules.sort(key=lambda r: -len(r[1].pattern))
    _operation_log_rules = rules
    print(f"[OperationLogMiddleware] 已加载 {len(rules)} 条操作日志规则")


def _match_action(method: str, path: str) -> str | None:
    """
    根据 HTTP method + path 匹配日志规则。
    返回 action_name 或 None（不记录日志）。
    """
    for rule_method, regex, name in _operation_log_rules:
        if rule_method == method and regex.match(path):
            return name
    return None


# ──────────────────────────────────────────────
#  Middleware
# ──────────────────────────────────────────────


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    全局 JWT 认证中间件。
    白名单路径无需登录，其余所有路径必须携带合法的 Authorization: Bearer <token>。
    """

    # 无需认证的路由（method, path）
    WHITE_LIST: set = {
        ("POST", "/auth/login"),
        ("GET",  "/"),
        ("GET",  "/docs"),
        ("GET",  "/openapi.json"),
        ("GET",  "/redoc"),
    }

    async def dispatch(self, request: Request, call_next):
        # 1. IP 白名单放行（如：本地或创始人 IP）
        client_ip = request.client.host if request.client else ""

        if client_ip in whitelist_ips:
            return await call_next(request)

        # 2. 路径白名单放行
        key = (request.method, request.url.path)
        if key in self.WHITE_LIST:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "未登录，请先获取 Token"},
            )

        token = auth_header.split(" ", 1)[1]
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token 已过期，请重新登录"},
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token 无效"},
            )

        return await call_next(request)


class OperationLogMiddleware(BaseHTTPMiddleware):
    """全局操作日志中间件：根据硬编码规则自动匹配并记录操作日志"""

    async def dispatch(self, request: Request, call_next):
        # 只拦截写操作
        if request.method not in ("POST", "PUT", "DELETE", "PATCH"):
            return await call_next(request)

        path = request.url.path
        action_name = _match_action(request.method, path)
        if action_name is None:
            return await call_next(request)

        start_time = time.time()

        # ── 读取 request body ──
        req_body_bytes = await request.body()
        req_json = None
        try:
            req_json = json.loads(req_body_bytes) if req_body_bytes else None
        except Exception:
            req_json = None

        # 登录请求脱敏密码
        if req_json and "password" in (req_json or {}):
            req_json = {k: ("***" if k == "password" else v) for k, v in req_json.items()}

        # ── 调用下游处理 ──
        response: Response = await call_next(request)

        # ── 读取 response body ──
        resp_body_bytes = b""
        async for chunk in response.body_iterator:
            if isinstance(chunk, str):
                resp_body_bytes += chunk.encode("utf-8")
            else:
                resp_body_bytes += chunk

        resp_json = None
        try:
            resp_json = json.loads(resp_body_bytes) if resp_body_bytes else None
        except Exception:
            resp_json = None

        # ── 解析 user_id ──
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
                if username:
                    db = SessionLocal()
                    try:
                        user = get_user_by_username(db, username=username)
                        if user:
                            user_id = user.id
                    finally:
                        db.close()
            except Exception:
                pass

        # 登录成功时从响应或请求体推断 user_id
        if user_id is None and resp_json and response.status_code == 200:
            login_username = resp_json.get("username") or (req_json or {}).get("username")
            if login_username:
                db = SessionLocal()
                try:
                    user = get_user_by_username(db, username=login_username)
                    if user:
                        user_id = user.id
                finally:
                    db.close()

        # ── 写入日志 ──
        latency_ms = int((time.time() - start_time) * 1000)
        status_code = response.status_code
        success = 1 if 200 <= status_code < 400 else 0
        error_message = None
        if not success and resp_json:
            error_message = resp_json.get("detail", str(resp_json))

        db = SessionLocal()
        try:
            operation_log_service.create_log(
                db,
                user_id=user_id,
                action=action_name,
                method=request.method,
                path=path,
                ip=request.headers.get("X-Client-IP") or (request.client.host if request.client else None),
                user_agent=request.headers.get("user-agent"),
                status_code=status_code,
                success=success,
                request_body=req_json,
                response_body=resp_json,
                latency_ms=latency_ms,
                error_message=error_message,
            )
        except Exception as e:
            print(f"[OperationLogMiddleware] 日志写入异常: {e}")
        finally:
            db.close()

        # 重建 response（body_iterator 已被消费，必须重新构造）
        return Response(
            content=resp_body_bytes,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )


# ──────────────────────────────────────────────
#  App
# ──────────────────────────────────────────────

app = FastAPI(title="FastAPI Backend")

# 注册中间件
# 注意：FastAPI/Starlette 中间件「后注册先执行」
# JWTAuthMiddleware 后注册，优先拦截请求做认证；认证通过后再由 OperationLogMiddleware 记录日志
app.add_middleware(OperationLogMiddleware)
app.add_middleware(JWTAuthMiddleware)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(operation_log_router)
app.include_router(role_menu_router)


@app.on_event("startup")
def on_startup():
    """应用启动时自动创建所有数据库表（如果不存在）"""
    Base.metadata.create_all(bind=engine)
    # 启动时编译操作日志规则
    _compile_log_rules()


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
