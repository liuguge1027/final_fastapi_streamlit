"""报表数据库配置"""
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class ReportDatabaseConfig(BaseSettings):
    """报表数据库配置"""

    # 默认使用主数据库（系统管理数据库）
    USE_MAIN_DB: bool = True

    # 报表专用数据库配置（可选）
    REPORT_DB_TYPE: str = "mysql"  # mysql, clickhouse, postgresql
    REPORT_DB_HOST: str = "127.0.0.1"
    REPORT_DB_PORT: int = 3306
    REPORT_DB_NAME: str = "report_db"
    REPORT_DB_USER: str = "root"
    REPORT_DB_PASSWORD: str = ""

    # 其他数据库配置
    REPORT_DB_POOL_SIZE: int = 5
    REPORT_DB_MAX_OVERFLOW: int = 10
    REPORT_DB_POOL_RECYCLE: int = 3600

    # 是否启用SSL
    REPORT_DB_SSL: bool = False

    # 自定义连接字符串（优先级最高）
    REPORT_DB_URL: Optional[str] = None

    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        if self.REPORT_DB_URL:
            return self.REPORT_DB_URL

        if self.USE_MAIN_DB:
            # 使用主数据库配置
            from .config import settings
            return settings.DATABASE_URL

        # 构建报表数据库URL
        if self.REPORT_DB_TYPE == "mysql":
            return f"mysql+pymysql://{self.REPORT_DB_USER}:{self.REPORT_DB_PASSWORD}@{self.REPORT_DB_HOST}:{self.REPORT_DB_PORT}/{self.REPORT_DB_NAME}"
        elif self.REPORT_DB_TYPE == "clickhouse":
            return f"clickhouse://{self.REPORT_DB_USER}:{self.REPORT_DB_PASSWORD}@{self.REPORT_DB_HOST}:{self.REPORT_DB_PORT}/{self.REPORT_DB_NAME}"
        else:
            raise ValueError(f"不支持的数据库类型: {self.REPORT_DB_TYPE}")

    model_config = ConfigDict(
        env_file=".env",
        env_prefix="REPORT_DB_"
    )


# 全局配置实例
report_config = ReportDatabaseConfig()