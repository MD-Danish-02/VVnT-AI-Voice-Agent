from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "VVnT AI Voice Agent"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    database_url: str = "postgresql+asyncpg://vvnt_user:vvnt_password@localhost:5432/vvnt_voice_agent"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "development-only-change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if not (self.redis_url.startswith("redis://") or self.redis_url.startswith("rediss://")):
            raise ValueError(
                f"Invalid REDIS_URL scheme: '{self.redis_url}'. Must begin with 'redis://' or 'rediss://'."
            )

        allowed_algorithms = {"HS256", "HS384", "HS512"}
        if self.jwt_algorithm not in allowed_algorithms:
            raise ValueError(
                f"Unsupported or insecure JWT algorithm: '{self.jwt_algorithm}'. "
                f"Allowed algorithms: {sorted(allowed_algorithms)}"
            )

        if self.access_token_expire_minutes <= 0:
            raise ValueError("access_token_expire_minutes must be greater than 0")

        insecure_dev_secrets = {
            "development-only-change-this-secret",
            "secret",
            "changeme",
            "jwt-secret",
        }
        is_production = self.environment.strip().lower() in {"production", "prod", "staging"}
        if is_production:
            if (
                not self.jwt_secret_key
                or self.jwt_secret_key in insecure_dev_secrets
                or len(self.jwt_secret_key) < 32
            ):
                raise ValueError(
                    "In production/staging environments, jwt_secret_key must be configured with a secure, "
                    "non-default secret of at least 32 characters."
                )
        return self


settings = Settings()