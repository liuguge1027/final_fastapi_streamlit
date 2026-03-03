from sqlalchemy import (
    Column, BigInteger, String, Text, Integer, JSON, DateTime, func, ForeignKey,
)
from sqlalchemy.orm import relationship
from backend.db.database import Base


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, comment="操作用户ID")
    action = Column(String(100), nullable=False, comment="操作名称，如 create_user")
    method = Column(String(20), nullable=False, comment="HTTP方法，如 GET/POST")
    path = Column(String(255), nullable=False, comment="请求路径")
    ip = Column(String(50), nullable=True, comment="用户 IP")
    user_agent = Column(Text, nullable=True, comment="User-Agent")
    status_code = Column(Integer, nullable=False, comment="HTTP状态码")
    success = Column(Integer, nullable=False, default=1, comment="是否成功（1:成功, 0:失败）")
    request_body = Column(JSON, nullable=True, comment="请求体")
    response_body = Column(JSON, nullable=True, comment="响应体")
    latency_ms = Column(Integer, nullable=True, comment="请求耗时（毫秒）")
    error_message = Column(Text, nullable=True, comment="异常信息")
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )

    # 关联用户
    user = relationship("User", back_populates="operation_logs")

    def __repr__(self):
        return f"<OperationLog(id={self.id}, action='{self.action}', ip='{self.ip}')>"
