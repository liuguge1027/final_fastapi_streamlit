"""报表服务层"""
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from jinja2 import Template
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.core.report_config import report_config
from backend.db.database import SessionLocal as MainSessionLocal


class ReportService:
    """报表服务"""

    def __init__(self):
        self.base_sql_path = Path(__file__).parent.parent / "reports"

    def _get_sql_file_path(self, module: str, report_name: str) -> Path:
        """获取SQL文件路径"""
        # 支持两种路径格式：1) module/sql/report_name.sql 2) module/report_name.sql
        sql_path = self.base_sql_path / module / "sql" / f"{report_name}.sql"
        if sql_path.exists():
            return sql_path

        # 尝试直接路径
        sql_path = self.base_sql_path / module / f"{report_name}.sql"
        if sql_path.exists():
            return sql_path

        raise FileNotFoundError(f"报表SQL文件不存在: {module}/{report_name}.sql")

    def _render_sql_template(self, sql_template: str, params: Dict[str, Any]) -> str:
        """渲染SQL模板，支持Jinja2语法和参数绑定"""
        # 使用Jinja2渲染条件语句
        template = Template(sql_template)
        rendered = template.render(**params)

        # 替换命名参数为SQLAlchemy的绑定参数格式（:param_name）
        # 这里我们保持Jinja2渲染后的SQL，参数绑定由SQLAlchemy处理
        return rendered

    def _get_db_session(self) -> Session:
        """获取数据库会话"""
        # 暂时使用主数据库会话
        # TODO: 支持多数据源
        return MainSessionLocal()

    async def execute_report(
        self,
        module: str,
        report_name: str,
        params: Optional[Dict[str, Any]] = None,
        db_session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        执行报表查询

        Args:
            module: 模块名称，如 'hr', 'finance', 'sales'
            report_name: 报表名称，对应SQL文件名
            params: 查询参数
            db_session: 可选的数据库会话，默认为主数据库

        Returns:
            Dict: 包含查询结果和元数据
        """
        if params is None:
            params = {}

        try:
            # 1. 读取SQL文件
            sql_path = self._get_sql_file_path(module, report_name)
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_template = f.read()

            # 2. 渲染SQL模板
            rendered_sql = self._render_sql_template(sql_template, params)

            # 3. 执行查询
            use_external_session = db_session is not None
            if not db_session:
                db_session = self._get_db_session()

            try:
                # 执行查询
                result = db_session.execute(text(rendered_sql), params)
                rows = result.fetchall()

                # 转换为字典列表
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in rows]

                # 获取总数（如果有分页）
                total_count = len(data)
                if "limit" in params and "offset" in params:
                    # 如果有分页参数，获取总记录数（去掉limit和offset）
                    count_sql = re.sub(
                        r'LIMIT\s+\:?\w+\s*(OFFSET\s+\:?\w+)?',
                        '',
                        rendered_sql,
                        flags=re.IGNORECASE
                    )
                    count_sql = f"SELECT COUNT(*) as total FROM ({count_sql}) as subquery"
                    total_result = db_session.execute(text(count_sql), params)
                    total_count = total_result.scalar() or 0

                return {
                    "success": True,
                    "data": data,
                    "total": total_count,
                    "module": module,
                    "report_name": report_name,
                    "generated_at": datetime.now().isoformat(),
                    "params": params
                }

            finally:
                # 如果是内部创建的会话，需要关闭
                if not use_external_session and db_session:
                    db_session.close()

        except FileNotFoundError as e:
            raise ValueError(f"报表不存在: {e}")
        except Exception as e:
            # 记录错误日志
            import traceback
            error_details = traceback.format_exc()
            print(f"报表执行失败: {e}\n{error_details}")
            raise RuntimeError(f"报表查询失败: {str(e)}")

    def get_available_reports(self) -> Dict[str, List[str]]:
        """获取可用报表列表"""
        reports = {}
        if not self.base_sql_path.exists():
            return reports

        for module_dir in self.base_sql_path.iterdir():
            if module_dir.is_dir():
                module_name = module_dir.name
                sql_files = []

                # 查找sql目录下的.sql文件
                sql_dir = module_dir / "sql"
                if sql_dir.exists():
                    sql_files = [
                        f.stem for f in sql_dir.glob("*.sql")
                        if f.is_file()
                    ]

                # 查找直接放在模块目录下的.sql文件
                direct_files = [
                    f.stem for f in module_dir.glob("*.sql")
                    if f.is_file()
                ]

                all_files = list(set(sql_files + direct_files))
                if all_files:
                    reports[module_name] = sorted(all_files)

        return reports


# 全局服务实例
report_service = ReportService()