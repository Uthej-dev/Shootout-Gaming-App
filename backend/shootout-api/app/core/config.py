from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    mongodb_url: str
    database_name: str = "ShootOut"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    dev_signup_bonus: int = 0
    local_timezone: str = "Asia/Kolkata"


settings = Settings()
