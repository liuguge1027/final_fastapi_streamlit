from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # 每次拿连接前检查是否可用，防止 MySQL gone away
    pool_recycle=3600,       # 1小时回收连接，防止被 MySQL 杀死
    pool_size=10,            # 核心连接池大小
    max_overflow=20          # 超过核心连接池后最多还能创建的连接数
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
