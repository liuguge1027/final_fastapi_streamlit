"""报表数据API"""
import io
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
import json
import pandas as pd

from backend.db.database import get_db
from backend.core.auth import get_current_user
from backend.services.report_service import report_service

router = APIRouter(
    prefix="/reports",
    tags=["报表数据"],
    dependencies=[Depends(get_current_user)]  # 需要登录认证
)


@router.get("/")
async def list_available_reports():
    """获取所有可用报表列表"""
    try:
        reports = report_service.get_available_reports()
        return {
            "success": True,
            "data": reports,
            "message": "获取报表列表成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取报表列表失败: {str(e)}")


@router.get("/{module}/{report_name}")
async def execute_report(
    request: Request,
    module: str,
    report_name: str,
    db: Session = Depends(get_db),
    # 通用查询参数
    page: Optional[int] = Query(1, ge=1, description="页码"),
    page_size: Optional[int] = Query(100, ge=1, le=1000, description="每页大小"),
    format: str = Query("json", pattern="^(json|csv)$", description="返回格式"),
    # 动态参数：从查询字符串中收集所有其他参数
):
    """执行指定报表查询

    支持任意查询参数，参数会自动传递给SQL模板。
    例如：/reports/hr/employee_statistics?department=技术部&start_date=2024-01-01
    """
    try:
        # 收集所有查询参数（排除page、page_size、format等系统参数）
        exclude_params = {"page", "page_size", "format", "module", "report_name"}
        params = {}
        for key, value in request.query_params.items():
            if key not in exclude_params:
                # 尝试解析JSON值
                try:
                    if value.startswith("{") or value.startswith("["):
                        params[key] = json.loads(value)
                    else:
                        params[key] = value
                except (json.JSONDecodeError, AttributeError):
                    params[key] = value

        # 添加分页参数
        if page and page_size:
            params["page"] = page
            params["page_size"] = page_size
            params["limit"] = page_size
            params["offset"] = (page - 1) * page_size

        # 执行报表查询
        result = await report_service.execute_report(
            module=module,
            report_name=report_name,
            params=params,
            db_session=db
        )

        # 格式转换
        if format == "csv":
            df = pd.DataFrame(result["data"])
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_data = csv_buffer.getvalue()

            return {
                "success": True,
                "data": csv_data,
                "format": "csv",
                "filename": f"{module}_{report_name}_page{page}.csv",
                "total": result["total"],
                "page": page,
                "page_size": page_size
            }
        else:
            return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报表查询失败: {str(e)}")


@router.get("/{module}/{report_name}/params")
async def get_report_params(module: str, report_name: str):
    """获取报表参数定义（需要手动定义，暂时返回空）"""
    # TODO: 可以从SQL文件注释中解析参数定义
    return {
        "success": True,
        "module": module,
        "report_name": report_name,
        "params": [],
        "message": "参数定义需要手动配置"
    }