from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Q-Identity"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./qidentity.db"

    BLOCKCHAIN_RPC_URL: str = "http://127.0.0.1:8545"
    BLOCKCHAIN_CHAIN_ID: int = 31337
    CONTRACT_ADDRESS: str = ""
    CONTRACT_DEPLOYMENT_BLOCK: int = 0

    JWT_SECRET: str = "q-identity-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    CHALLENGE_EXPIRATION_SECONDS: int = 300
    MAX_AUTH_ATTEMPTS: int = 5

    DEFAULT_CRYPTO_ALGORITHM: str = "ECDSA"
    SUPPORTED_ALGORITHMS: list[str] = ["ECDSA", "HYBRID", "ML-DSA"]

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
