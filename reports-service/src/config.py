"""
Configuration settings for the Reports Service
"""
import os
from typing import Optional, List
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database Configuration
    database_url: str = "mysql+pymysql://user:password@localhost:3306/ong_management"
    database_echo: bool = False
    
    # SOAP Service Configuration
    SOAP_SERVICE_URL: str = "https://soap-applatest.onrender.com/?wsdl"
    SOAP_TIMEOUT: int = 30
    
    # Excel Storage Configuration
    excel_storage_path: str = "./storage/excel"
    excel_file_expiry_hours: int = 24
    
    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def cors_origins_list(self) -> list:
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings