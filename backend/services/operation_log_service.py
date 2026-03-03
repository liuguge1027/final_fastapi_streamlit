"""操作日志业务逻辑层"""
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.models.operation_log import OperationLog
from backend.schemas.operation_log_schema import OperationLogCreate
from backend.crud import crud_operation_log


def get_operation_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[OperationLog]:
    """获取操作日志列表"""
    return crud_operation_log.get_operation_logs(
        db, skip=skip, limit=limit,
        user_id=user_id, start_date=start_date, end_date=end_date,
    )


def get_operation_log_by_id(db: Session, log_id: int) -> Optional[OperationLog]:
    """根据ID获取操作日志"""
    return crud_operation_log.get_operation_log_by_id(db, log_id)


def create_operation_log(db: Session, log_data: OperationLogCreate) -> OperationLog:
    """创建操作日志"""
    return crud_operation_log.create_operation_log(db, log_data)


def delete_logs_before_days(db: Session, days: int) -> int:
    """删除指定天数之前的操作日志，返回删除条数"""
    return crud_operation_log.delete_logs_before_days(db, days)


def create_log(
    db: Session,
    *,
    user_id: Optional[int],
    action: str,
    method: str,
    path: str,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    status_code: int = 200,
    success: int = 1,
    request_body=None,
    response_body=None,
    latency_ms: Optional[int] = None,
    error_message: Optional[str] = None,
):
    """便捷方法：直接传参写入操作日志（供 middleware 调用）"""
    import json
    # 安全序列化
    req_json = None
    if request_body is not None:
        try:
            req_json = json.loads(json.dumps(request_body, default=str))
        except Exception:
            req_json = None

    resp_json = None
    if response_body is not None:
        try:
            resp_json = json.loads(json.dumps(response_body, default=str))
        except Exception:
            resp_json = None

    log_data = OperationLogCreate(
        user_id=user_id,
        action=action,
        method=method,
        path=path,
        ip=ip,
        user_agent=user_agent,
        status_code=status_code,
        success=success,
        request_body=req_json,
        response_body=resp_json,
        latency_ms=latency_ms,
        error_message=error_message,
    )
    try:
        return crud_operation_log.create_operation_log(db, log_data)
    except Exception as e:
        print(f"[OperationLog] 日志写入失败: {e}")
        return None
