from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./dev.db"
    redis_url: str = "redis://redis:6379/0"
    oss_endpoint: str = ""
    oss_bucket: str = ""
    oss_access_key_id: str = ""
    oss_access_key_secret: str = ""
    tencent_secret_id: str = ""
    tencent_secret_key: str = ""
    tencent_region: str = "ap-beijing"

settings = Settings()
