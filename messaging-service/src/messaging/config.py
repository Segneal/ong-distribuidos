import os
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    # Kafka Configuration
    kafka_bootstrap_servers: List[str] = Field(
        default_factory=lambda: os.getenv("KAFKA_BROKERS", "kafka:9092").split(",")
    )
    kafka_group_id: str = Field(default_factory=lambda: os.getenv("KAFKA_GROUP_ID", "empuje-comunitario-group"))
    kafka_retry_attempts: int = Field(default_factory=lambda: int(os.getenv("KAFKA_RETRY_ATTEMPTS", "3")))
    kafka_retry_delay: int = Field(default_factory=lambda: int(os.getenv("KAFKA_RETRY_DELAY", "1000")))
    kafka_max_retry_delay: int = Field(default_factory=lambda: int(os.getenv("KAFKA_MAX_RETRY_DELAY", "10000")))
    kafka_auto_create_topics: bool = Field(default_factory=lambda: os.getenv("KAFKA_AUTO_CREATE_TOPICS", "true").lower() == "true")
    kafka_replication_factor: int = Field(default_factory=lambda: int(os.getenv("KAFKA_REPLICATION_FACTOR", "1")))
    kafka_enabled: bool = Field(default_factory=lambda: os.getenv("KAFKA_ENABLED", "true").lower() == "true")
    
    # Organization Configuration
    organization_id: str = Field(default_factory=lambda: os.getenv("ORGANIZATION_ID", "empuje-comunitario"))
    
    # Database Configuration (MySQL)
    db_host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_port: int = Field(default_factory=lambda: int(os.getenv("DB_PORT", "3306")))
    db_name: str = Field(default_factory=lambda: os.getenv("DB_NAME", "ong_management"))
    db_user: str = Field(default_factory=lambda: os.getenv("DB_USER", "root"))
    db_password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", "root"))
    
    # Service Configuration
    service_port: int = Field(default_factory=lambda: int(os.getenv("SERVICE_PORT", "50054")))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


# Global settings instance
settings = Settings()


# Topic definitions
class Topics:
    DONATION_REQUESTS = "solicitud-donaciones"
    DONATION_TRANSFERS = "transferencia-donaciones"
    DONATION_OFFERS = "oferta-donaciones"
    REQUEST_CANCELLATIONS = "baja-solicitud-donaciones"
    SOLIDARITY_EVENTS = "eventossolidarios"
    EVENT_CANCELLATIONS = "baja-evento-solidario"
    EVENT_ADHESIONS = "adhesion-evento"
    
    @classmethod
    def get_transfer_topic(cls, org_id: str) -> str:
        return f"{cls.DONATION_TRANSFERS}-{org_id}"
    
    @classmethod
    def get_adhesion_topic(cls, org_id: str) -> str:
        return f"{cls.EVENT_ADHESIONS}-{org_id}"