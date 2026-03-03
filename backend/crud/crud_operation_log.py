"""操作日志 CRUD 数据库操作层"""
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from datetime import datetime, timedelta
from backend.models.operation_log import OperationLog
from backend.schemas.operation_log_schema import OperationLogCreate

def create_operation_log(db: Session, log_data: OperationLogCreate) -> OperationLog:
    """创建操作日志"""
    db_log = OperationLog(
        user_id=log_data.user_id,
        action=log_data.action,
        method=log_data.method,
        path=log_data.path,
        ip=log_data.ip,
        user_agent=log_data.user_agent,
        status_code=log_data.status_code,
        success=log_data.success,
        request_body=log_data.request_body,
        response_body=log_data.response_body,
        latency_ms=log_data.latency_ms,
        error_message=log_data.error_message,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_operation_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[OperationLog]:
    """获取操作日志列表（支持按用户和时间过滤）"""
    query = db.query(OperationLog).options(selectinload(OperationLog.user))

    if user_id is not None:
        query = query.filter(OperationLog.user_id == user_id)

    if start_date:
        try:
            dt = datetime.fromisoformat(start_date)
            query = query.filter(OperationLog.created_at >= dt)
        except ValueError:
            pass

    if end_date:
        try:
            dt = datetime.fromisoformat(end_date)
            # 包含结束日期当天
            dt = dt + timedelta(days=1)
            query = query.filter(OperationLog.created_at < dt)
        except ValueError:
            pass

    return query.order_by(OperationLog.created_at.desc()).offset(skip).limit(limit).all()


def get_operation_log_by_id(db: Session, log_id: int) -> Optional[OperationLog]:
    """根据ID获取操作日志"""
    return (
        db.query(OperationLog)
        .options(selectinload(OperationLog.user))
        .filter(OperationLog.id == log_id)
        .first()
    )


def delete_logs_before_days(db: Session, days: int) -> int:
    """删除指定天数之前的操作日志，返回删除条数"""
    # 采用"零点"作为分界线，更符合用户感知的"昨天"、"7天前"
    # days=1: 删除今天 00:00 之前的日志 (即删除昨天及更早的)
    # days=7: 删除 7 天前(从今天起算) 00:00 之前的日志
    today_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff = today_midnight - timedelta(days=days-1)
    
    count = db.query(OperationLog).filter(OperationLog.created_at < cutoff).delete()
    db.commit()
    return count
