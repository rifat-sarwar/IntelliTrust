from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os

class Settings(BaseSettings):
    # Application Settings
    PROJECT_NAME: str = "IntelliTrust"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:1234@localhost:5432/intellitrust"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File Storage (S3/MinIO)
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY_ID: str = "minioadmin"
    S3_SECRET_ACCESS_KEY: str = "minioadmin123"
    S3_BUCKET_NAME: str = "intellitrust-documents"
    S3_REGION: str = "us-east-1"
    
    # AI Engine
    AI_ENGINE_URL: str = "http://localhost:8001"
    AI_MODEL_PATH: str = "/app/models"
    
    # Blockchain (Hyperledger Fabric)
    FABRIC_CA_URL: str = "http://localhost:7054"
    FABRIC_NETWORK_CONFIG_PATH: str = "./blockchain/network-config"
    FABRIC_CHANNEL_NAME: str = "intellitrust-channel"
    FABRIC_CHAINCODE_NAME: str = "document-chaincode"
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Webhook Configuration
    WEBHOOK_SECRET: str = "your-webhook-secret"
    WEBHOOK_URL: Optional[str] = None
    
    # Monitoring and Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Document Processing
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "jpg", "jpeg", "png", "tiff"]
    DOCUMENT_PROCESSING_TIMEOUT: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
