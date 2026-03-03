import re
import time
import json
import jwt

from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.db.database import Base, engine, SessionLocal
from backend.models.user import User  # noqa: F401
from backend.models.role import Role  # noqa: F401
from backend.models.permission import Permission  # noqa: F401
from backend.models.role_permission import RolePermission  # noqa: F401
from backend.models.operation_log import OperationLog  # noqa: F401

from backend.api.auth import router as auth_router
from backend.api.user_api import router as user_router
from backend.api.role_api import router as role_router
from backend.api.permission_api import router as permission_router
from backend.api.operation_log_api import router as operation_log_router

from backend.core.security import SECRET_KEY, ALGORITHM
from backend.services.user_service import get_user_by_username
from backend.services import operation_log_service


# ──────────────────────────────────────────────
#  权限路径匹配工具
# ──────────────────────────────────────────────

def _path_to_regex(path_template: str) -> re.Pattern:
    """
    将权限表中的路径模板转为正则:
      /users/{id}             →  ^/users/[^/]+$
      /roles/{id}/permissions →  ^/roles/[^/]+/permissions$
    """
    # 把 {xxx} 替换为 [^/]+
    pattern = re.sub(r"\{[^}]+\}", r"[^/]+", path_template)
    return re.compile(f"^{pattern}$")


# 缓存：[(method, compiled_regex, permission_name, permission_code), ...]
_permission_rules: list[tuple[str, re.Pattern, str, str]] = []
_rules_loaded = False


def _load_permission_rules():
    """从 permissions 表加载 type='api' 的记录，编译为匹配规则（仅加载一次）"""
    global _permission_rules, _rules_loaded
    db = SessionLocal()
    try:
        api_perms = (
            db.query(Permission)
            .filter(Permission.type == "api")
            .filter(Permission.path.isnot(None))
            .filter(Permission.method.isnot(None))
            .all()
        )
        rules = []
        for p in api_perms:
            regex = _path_to_regex(p.path.strip())
            rules.append((p.method.upper().strip(), regex, p.name, p.code))
        # 按路径长度降序排列，优先匹配更具体的路径
        rules.sort(key=lambda r: -len(r[1].pattern))
        _permission_rules = rules
        _rules_loaded = True
        print(f"[OperationLogMiddleware] 已加载 {len(rules)} 条 API 权限规则")
    except Exception as e:
        print(f"[OperationLogMiddleware] 加载权限规则失败: {e}")
    finally:
        db.close()


def reload_permission_rules():
    """外部调用：强制重新加载权限规则（如权限表有变更时）"""
    global _rules_loaded
    _rules_loaded = False
    _load_permission_rules()


def _match_action(method: str, path: str) -> tuple[str, str] | None:
    """
    根据 HTTP method + path 匹配权限规则。
    返回 (permission_name, permission_code) 或 None（不记录日志）。
    """
    if not _rules_loaded:
        _load_permission_rules()
    for rule_method, regex, name, code in _permission_rules:
        if rule_method == method and regex.match(path):
            return name, code
    return None


# ──────────────────────────────────────────────
#  Middleware
# ──────────────────────────────────────────────

class OperationLogMiddleware(BaseHTTPMiddleware):
    """全局操作日志中间件：根据 permissions 表自动匹配并记录操作日志"""

    async def dispatch(self, request: Request, call_next):
        # 只拦截写操作
        if request.method not in ("POST", "PUT", "DELETE", "PATCH"):
            return await call_next(request)

        path = request.url.path
        match = _match_action(request.method, path)
        if match is None:
            return await call_next(request)

        action_name, action_code = match
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
                ip=request.client.host if request.client else None,
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
app.add_middleware(OperationLogMiddleware)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(permission_router)
app.include_router(operation_log_router)


@app.on_event("startup")
def on_startup():
    """应用启动时自动创建所有数据库表（如果不存在）"""
    Base.metadata.create_all(bind=engine)
    # 启动时预加载权限规则
    _load_permission_rules()


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
