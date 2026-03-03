"""用户相关 Pydantic Schema"""
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录成功响应"""
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    is_superuser: bool


class UserBase(BaseModel):
    """用户基础信息"""
    username: str
    email: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is None or v == "":
            return None
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v


class UserCreate(UserBase):
    """创建用户请求"""
    password: str
    role_id: Optional[int] = None
    is_active: Optional[int] = 1
    is_superuser: Optional[int] = 0


class UserUpdate(BaseModel):
    """更新用户请求"""
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[int] = None
    is_superuser: Optional[int] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is None or v == "":
            return None
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v


class UserInfo(UserBase):
    """用户详细信息"""
    id: int
    role_id: Optional[int] = None
    is_active: int
    is_superuser: int
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserDetail(UserInfo):
    """用户详情（包含角色信息）"""
    role_name: Optional[str] = None
    role_code: Optional[str] = None
