from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "VVnT AI Voice Agent"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://vvnt_user:vvnt_password@localhost:5432/vvnt_voice_agent"
    
    class Config:
        env_file = ".env"


settings = Settings()