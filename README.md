# Final FastAPI + Streamlit Project

这是一个结合了FastAPI后端和Streamlit前端的完整项目，提供了用户认证、角色权限管理、财务管理、人力资源管理和销售管理等功能。

## 项目架构

### 技术栈
- **后端**：FastAPI + SQLAlchemy + MySQL + JWT
- **前端**：Streamlit + Streamlit-Cookies-Manager
- **数据库迁移**：Alembic
- **认证**：JWT Token + 加密Cookie

### 项目结构

```
├── backend/           # FastAPI后端应用
│   ├── api/           # API路由
│   ├── core/          # 核心配置和工具
│   ├── crud/          # 数据库操作
│   ├── db/            # 数据库连接
│   ├── models/        # 数据模型
│   ├── schemas/       # 数据验证和序列化
│   ├── services/      # 业务逻辑
│   ├── utils/         # 工具函数
│   └── main.py        # 后端入口
├── frontend/          # Streamlit前端应用
│   ├── components/    # 可复用组件
│   ├── ui/            # UI模板
│   ├── utils/         # 工具函数
│   ├── views/         # 页面视图
│   │   ├── admin/     # 管理员页面
│   │   ├── auth/      # 认证页面
│   │   ├── finance/   # 财务页面
│   │   ├── hr/        # 人力资源页面
│   │   ├── manager/   # 经理页面
│   │   ├── sale/      # 销售页面
│   │   └── user/      # 用户页面
│   └── app.py         # 前端入口
├── scripts/           # 启动脚本
├── alembic/           # 数据库迁移
├── README/            # 项目文档
├── .gitignore         # Git忽略文件
├── alembic.ini        # Alembic配置
├── init_db.py         # 数据库初始化脚本
├── migrate_db.py      # 数据库迁移脚本
├── requirements.txt   # 项目依赖
└── README.md          # 项目说明
```

## 快速开始

### 1. 环境要求
- Python 3.9+
- MySQL 5.7+

### 2. 安装步骤

#### 2.1 克隆项目
```bash
git clone https://github.com/liuguge1027/final_fastapi_streamlit.git
cd final_fastapi_streamlit
```

#### 2.2 创建虚拟环境
```bash
python3 -m venv .venv
```

#### 2.3 激活虚拟环境
- **MacOS/Linux**:
  ```bash
  source .venv/bin/activate
  ```
- **Windows**:
  ```bash
  .venv\Scripts\activate
  ```

#### 2.4 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 数据库配置

#### 3.1 修改数据库连接信息
编辑 `backend/core/config.py` 文件，修改以下配置：

```python
class Settings(BaseSettings):
    MYSQL_USER: str = "root"         # 数据库用户名
    MYSQL_PASSWORD: str = "mikesql."  # 数据库密码
    MYSQL_HOST: str = "127.0.0.1"     # 数据库主机
    MYSQL_PORT: int = 3306            # 数据库端口
    MYSQL_DB: str = "final_db"        # 数据库名称

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    model_config = ConfigDict(env_file=".env")
```

#### 3.2 初始化数据库
```bash
python init_db.py
```

#### 3.3 更新模型（当修改models时）
```bash
python migrate_db.py
```

#### 3.4 模型数据导入（首次初始化需要导入）
```bash
python seed_data.py
```### 4. 启动应用

#### 4.1 启动后端
```bash
./scripts/start_backend.sh
```
后端服务将运行在 `http://127.0.0.1:8000`

#### 4.2 启动前端
```bash
./scripts/start_frontend.sh
```
前端服务将运行在 `http://localhost:8501`

## 功能模块

### 1. 认证系统
- 用户注册和登录
- JWT Token认证
- 加密Cookie存储

### 2. 角色权限管理
- 角色创建和管理
- 权限分配
- 基于角色的访问控制

### 3. 财务管理
- 收入管理
- 支出管理
- 管理员专用功能

### 4. 人力资源管理
- 员工管理
- 绩效评估

### 5. 销售管理
- 客户管理
- 销售记录管理

## 开发指南

### 代码风格
- 遵循PEP 8编码规范
- 使用类型提示
- 模块化设计

### 数据库迁移
- 使用Alembic进行数据库迁移
- 运行 `python migrate_db.py` 自动检测模型变化并生成迁移

### 测试
- 运行单元测试：`pytest`
- 运行API文档：访问 `http://127.0.0.1:8000/docs`

## 部署

### 生产环境部署
1. 配置生产环境变量
2. 使用Gunicorn或Uvicorn运行后端
3. 使用Streamlit Server运行前端
4. 配置Nginx作为反向代理

### 环境变量
可以创建 `.env` 文件来覆盖默认配置：

```
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_HOST=your_host
MYSQL_PORT=3306
MYSQL_DB=your_database
```

## 常见问题

### 1. 数据库连接失败
- 检查MySQL服务是否运行
- 验证数据库配置是否正确
- 确保数据库用户有足够权限

### 2. 启动失败
- 检查端口是否被占用
- 验证依赖是否安装正确
- 查看日志获取详细错误信息

### 3. 权限问题
- 确保用户有正确的角色和权限
- 检查数据库中的角色权限配置

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用MIT许可证。
