# BaseSettings = Loads and validates configuration.
# SettingsConfigDict = Configures how configuration is loaded.
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "GitHub Code Analyzer API"
    DEBUG: bool = False
    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    # Defines a default value plus validation constraints.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=5, le=1440)

    FERNET_KEY: str
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://127.0.0.1:8000/api/v1/github/callback"
    GITHUB_OAUTH_STATE_SECRET: str

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    MAX_REPOSITORY_FILES: int = Field(default=40, ge=1, le=200)
    MAX_FILE_BYTES: int = Field(default=40000, ge=1000, le=200000)
    MAX_TOTAL_CODE_BYTES: int = Field(default=250000, ge=10000, le=2000000)
    MAX_ANALYSIS_CHARS_PER_CHUNK: int = Field(default=12000, ge=2000, le=30000)
    # Pydantic how to read your configuration
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
