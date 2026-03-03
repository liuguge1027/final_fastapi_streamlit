"""操作日志 API 路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.db.database import get_db
from backend.schemas.operation_log_schema import OperationLogRead
from backend.services import operation_log_service

router = APIRouter(prefix="/operation-logs", tags=["操作日志"])


@router.get("", response_model=List[OperationLogRead])
def get_operation_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取操作日志列表（支持按用户和时间过滤）"""
    return operation_log_service.get_operation_logs(
        db, skip=skip, limit=limit,
        user_id=user_id, start_date=start_date, end_date=end_date,
    )


@router.delete("/cleanup")
def cleanup_operation_logs(days: int = 7, db: Session = Depends(get_db)):
    """批量删除指定天数之前的操作日志"""
    if days < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="days 参数必须大于 0"
        )
    deleted_count = operation_log_service.delete_logs_before_days(db, days)
    return {"message": f"已删除 {deleted_count} 条日志", "deleted_count": deleted_count}


@router.get("/{log_id}", response_model=OperationLogRead)
def get_operation_log(log_id: int, db: Session = Depends(get_db)):
    """获取单条操作日志"""
    log = operation_log_service.get_operation_log_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )
    return log
