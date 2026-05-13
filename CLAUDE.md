# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

FastAPI + Streamlit 数据中台项目，采用前后端分离架构。后端提供 RESTful API，前端使用 Streamlit 构建交互式界面，支持基于角色（RBAC）的权限管理和全局操作日志记录。

## 快速启动

### 后端启动
```bash
./scripts/start_backend.sh
# 或直接运行
./.venv/bin/python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动
```bash
./scripts/start_frontend.sh
# 或直接运行
./.venv/bin/streamlit run frontend/app.py
```

### 数据库操作
```bash
python init_db.py      # 初始化数据库表结构
python migrate_db.py  # 数据库迁移（添加/修改模型后）
python seed_data.py    # 导入种子数据（管理员账户：admin / mikesql.）
```

## 架构说明

### 后端架构（三层设计）
1. **API 层** (`backend/api/`)：FastAPI 路由，处理 HTTP 请求
2. **Service 层** (`backend/services/`)：业务逻辑处理
3. **CRUD 层** (`backend/crud/`)：数据库原子操作

### 核心中间件
- **JWTAuthMiddleware**：全局 JWT 认证，支持 IP 白名单和路由白名单
- **OperationLogMiddleware**：自动记录 POST/PUT/DELETE 操作日志（硬编码规则在 main.py 的 `_OPERATION_LOG_RULES_RAW`）

### 前端架构
- **app.py**：统一入口，调用 `route_app()` 进行页面路由
- **router.py**：根据登录状态和角色动态加载页面
- **page_registry.py**：页面模块注册表，通过 `show_page()` 函数渲染页面
- **auth_utils.py**：使用 `streamlit-cookies-manager` 实现登录态持久化

## 添加新业务模块

参考 `README/add_module_tutorial.md`，按以下顺序创建：

1. **Model** (`backend/models/*.py`)：SQLAlchemy 数据模型
2. **Schema** (`backend/schemas/*_schema.py`)：Pydantic 数据校验
3. **CRUD** (`backend/crud/crud_*.py`)：数据库操作
4. **Service** (`backend/services/*_service.py`)：业务逻辑
5. **API** (`backend/api/*_api.py`)：FastAPI 路由
6. **挂载路由**：在 `backend/main.py` 中导入并 `app.include_router()`

## 配置说明

- 数据库配置：`backend/core/config.py` 或 `.env` 环境变量
- 默认管理员：admin / mikesql.
- 前端 API 地址：通过环境变量 `API_BASE_URL` 配置（默认 `/api`）

## 关键注意事项

- 所有数据库模型需在 `backend/main.py` 或 `backend/models/__init__.py` 中导入，确保 SQLAlchemy 能感知
- 新增操作日志规则需在 `main.py` 的 `_OPERATION_LOG_RULES_RAW` 中添加
- 前端页面模块必须包含 `show_page()` 函数
- JWT Token 存储在 Cookie + localStorage 中（双重保障，手机端兼容）