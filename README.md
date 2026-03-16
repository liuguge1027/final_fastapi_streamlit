# FastAPI + Streamlit 数据中台实战项目

这是一个企业级的前后端分离项目，集成了 **FastAPI** 高性能后端和 **Streamlit** 交互式前端。项目专注于 **自动化审计 (Auditing)**、**全局安全认证 (Security)** 和 **多租户权限管理 (RBAC)**，提供了一套开箱即用的管理系统模板。

---

## 🌟 核心亮点

- 🛡️ **全局 JWT 安全套件**：基于 FastAPI 中间件实现全局身份校验，支持 IP 白名单特权放行。
- 📝 **自动化全量审计**：内置 `OperationLogMiddleware`，自动记录所有非 GET 请求的操作细节（方法、路径、耗时、IP 及响应状态）。
- 📂 **全功能 RBAC 模型**：支持 用户 -> 角色 -> 权限 的细粒度控制。
- 🔄 **前端状态持久化**：使用 `streamlit-cookies-manager` 实现浏览器加密 Cookie 存储，解决 Streamlit 刷新即丢失状态的痛点。
- ⚡ **异步高性能架构**：后端全程基于异步 FastAPI 驱动，前端提供流畅的原生交互体验。

---

## 📂 项目结构

```text
├── backend/                # FastAPI 后端应用
│   ├── api/                # API 路由 (用户、角色、审计日志等)
│   ├── core/               # 核心层: auth (全局认证), security (JWT/加密), config
│   ├── crud/               # 数据库 CRUD 原子操作
│   ├── db/                 # 数据库连接与 Base 类
│   ├── models/             # SQLAlchemy 数据模型 (包含 OperationLog)
│   ├── schemas/            # Pydantic V2 校验模型
│   ├── services/           # 业务逻辑服务层
│   └── main.py             # 入口文件 (挂载全局中间件)
├── frontend/               # Streamlit 前端应用
│   ├── components/         # 自定义 UI 组件
│   ├── utils/              # 辅助工具 (auth_utils 实现持久化)
│   ├── views/              # 业务页面 (按权限模块划分)
│   └── app.py              # 前端统一入口与路由调度
├── scripts/                # 一键启动脚本 (Bash)
├── alembic/                # 数据库版本迁移管理
├── init_db.py              # 初始化数据库结构入口
├── migrate_db.py           # 自动化迁移生成工具
├── seed_data.py            # 基础数据 (超级管理员、角色) 预处理
└── requirements.txt        # 项目依赖清单
```

---

## 🚀 快速开始

### 1. 环境准备
- **Python**: 3.9+
- **MySQL**: 5.7+ (建议 8.0)

### 2. 初始化安装
```bash
# 克隆项目
git clone https://github.com/liuguge1027/final_fastapi_streamlit.git
cd final_fastapi_streamlit

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 后端配置与数据初始化
1.  **配置数据库**：在 `.env` 或 `backend/core/config.py` 中修改 `MYSQL_` 相关配置。
2.  **创建数据库表**：
    ```bash
    python init_db.py
    ```
3.  **导入种子数据**：
    ```bash
    python seed_data.py  # 预创建管理账户: admin / password: mikesql.
    ```

### 4. 运行应用
我们将启动过程封装在了 `/scripts` 下：

**启动后端 (Port 8000)**:
```bash
./scripts/start_backend.sh
```
*交互式 API 文档地址: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

**启动前端 (Port 8501)**:
```bash
./scripts/start_frontend.sh
```

---

## 🛠️ 技术内幕

### 全局认证 (backend/core/auth.py)
通过 `JWTAuthMiddleware` 拦截所有传入请求：
1. **IP 校验**：特定 IP（如 `127.0.0.1`）可跳过 Token 校验。
2. **白名单**：`/auth/login` 等公开接口不设限。
3. **Token 解析**：验证 JWT 有效性及过期时间。

### 自动化操作日志 (backend/main.py)
`OperationLogMiddleware` 会针对 `POST/PUT/DELETE` 请求自动执行：
- 记录执行用户 ID（从 Token 解析）。
- 捕获响应体中的错误信息。
- 计算业务处理耗时（Latency）。
- **密码脱敏**：敏感字段自动过滤，确保日志安全。

### 登录持久化 (frontend/utils/auth_utils.py)
利用 `EncryptedCookieManager` 将登录态同步至浏览器 Cookie。即使用户关闭浏览器或刷新页面，前端入口 `app.py` 也会通过 `check_login` 自动恢复 `st.session_state`。

---

## 📝 许可证
[MIT License](LICENSE)

## 🤝 贡献
欢迎 PR 和 Issue，让我们一起完善这个数据中台实战项目！
