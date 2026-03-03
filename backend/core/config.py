from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "mikesql."
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "final_db"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    model_config = ConfigDict(env_file=".env")
'''
class Settings(BaseSettings):
    MYSQL_USER: str = "admin"
    MYSQL_PASSWORD: str = "96.lbxxMIKE"
    MYSQL_HOST: str = "192.168.1.100"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "final_db"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    model_config = ConfigDict(env_file=".env")
'''
settings = Settings()
