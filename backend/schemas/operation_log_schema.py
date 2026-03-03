"""操作日志相关 Pydantic Schema"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any, Dict


# ---- 辅助 Schema ----

class UserBrief(BaseModel):
    """用户简要信息（仅 id + username，用于日志返回）"""
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


# ---- OperationLog Schema ----

class OperationLogCreate(BaseModel):
    """创建操作日志请求"""
    user_id: Optional[int] = None
    action: str
    method: str
    path: str
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    status_code: int
    success: int = 1
    request_body: Optional[Dict[str, Any]] = None
    response_body: Optional[Dict[str, Any]] = None
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None


class OperationLogRead(BaseModel):
    """操作日志详细信息（含关联用户简要）"""
    id: int
    user_id: Optional[int] = None
    action: str
    method: str
    path: str
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    status_code: int
    success: int
    request_body: Optional[Dict[str, Any]] = None
    response_body: Optional[Dict[str, Any]] = None
    latency_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    user: Optional[UserBrief] = None

    model_config = ConfigDict(from_attributes=True)
