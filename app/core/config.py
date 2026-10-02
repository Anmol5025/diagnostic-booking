from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    import os
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://myuser:mypassword@db/mydb")
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
