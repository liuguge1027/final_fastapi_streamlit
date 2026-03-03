# 项目文件结构 (Project File Structure)

本项目采用 **FastAPI (后端)** + **Streamlit (前端)** 的架构，实现了完整的 RBAC（基于角色的访问控制）权限管理系统和操作日志系统。

## 核心目录结构

### 1. Backend (后端 - FastAPI)
位于 `/backend` 目录下，遵循三层架构设计（API -> Service -> CRUD）。

*   **`main.py`**: **核心入口**。配置 FastAPI 实例、中间件以及路由。包含**全局操作日志中间件 (OperationLogMiddleware)**，通过匹配 `permissions` 表动态记录操作。
*   **`api/`**: **路由层 (Controller)**。定义 RESTful 接口。
    *   `auth.py`: 登录认证、Token 发放。
    *   `user_api.py`, `role_api.py`, `permission_api.py`: 基础数据管理。
    *   `operation_log_api.py`: 日志查询与批量清理（Cleanup）。
*   **`services/`**: **业务逻辑层 (Service)**。处理具体业务逻辑，如权限校验、日志构建等。
*   **`crud/`**: **数据访问层 (Repository)**。执行 SQLAlchemy 数据库操作。
*   **`models/`**: **ORM 模型**。定义 `User`, `Role`, `Permission`, `OperationLog` 等物理表结构。
*   **`schemas/`**: **Pydantic 模型**。定义输入输出数据格式，负责序列化与校验。
*   **`db/`**: 数据库配置。`database.py` 负责连接池与 Session 管理。
*   **`core/`**: 核心能力。`security.py` 处理 JWT 签发、验证及密码哈希。

### 2. Frontend (前端 - Streamlit)
位于 `/frontend` 目录下，通过 `api_client` 与后端交互。

*   **`app.py`**: **主程序**。负责整体布局逻辑和页面路由切换。
*   **`views/`**: **视图层**。
    *   `auth/`: 登录组件。
    *   `admin/pages/`: 管理模块页面（如 `operation_log_page.py` 包含日志展示与清除逻辑）。
*   **`utils/`**: **工具集**。
    *   `api_client.py`: 统一的后端请求封装。
    *   `auth_utils.py`: 前端 Token 状态持久化。
    *   `router.py`: 控制页面显示与跳转逻辑。

### 3. Database & Migrations (数据库管理)
*   **`alembic/`**: 数据库结构变更脚本（Migrations）。
*   **`init_db.py` / `seed_data.py`**: 初始化库表及插入超级管理员/初始权限数据的脚本。

### 4. Configuration & Docs (配置与文档)
*   **`requirements.txt`**: 项目环境依赖。
*   **`db.MD`**: 数据库详细设计文档。
*   **`README.md`**: 开发与部署指南。

---

## 关键机制流程
1.  **鉴权流程**: Login -> 后端生成 JWT -> 前端存储在浏览器缓存 -> 之后所有请求由 `api_client` 自动带上 `Authorization: Bearer <Token>`。
2.  **日志流程**: 用户请求 API -> 后端 Middleware 拦截 -> 匹配 `permissions` 表 -> 记录 `(用户ID, 动作名称, 请求参数, 返回状态)` 到 `operation_logs` 表。
3.  **动态菜单**: 前端加载时，根据用户所属角色的 `permissions` 列表，动态渲染侧边栏菜单及对应的渲染函数。
