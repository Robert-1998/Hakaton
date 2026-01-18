import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # API
    pollinations_timeout: int = int(os.getenv("POLLINATIONS_TIMEOUT", "60"))
    g4f_model: str = os.getenv("G4F_MODEL", "gpt-3.5-turbo")
    
    # Debug
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"  # backend/.env

settings = Settings()
