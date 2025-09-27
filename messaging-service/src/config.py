import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Kafka Configuration
    kafka_brokers: str = os.getenv("KAFKA_BROKERS", "kafka:9092")
    kafka_group_id: str = os.getenv("KAFKA_GROUP_ID", "empuje-comunitario-group")
    organization_id: str = os.getenv("ORGANIZATION_ID", "empuje-comunitario")
    
    # Kafka Retry Configuration
    kafka_retry_attempts: int = int(os.getenv("KAFKA_RETRY_ATTEMPTS", "3"))
    kafka_retry_delay: int = int(os.getenv("KAFKA_RETRY_DELAY", "1000"))
    kafka_max_retry_delay: int = int(os.getenv("KAFKA_MAX_RETRY_DELAY", "10000"))
    
    # Topic Configuration
    kafka_auto_create_topics: bool = os.getenv("KAFKA_AUTO_CREATE_TOPICS", "true").lower() == "true"
    kafka_replication_factor: int = int(os.getenv("KAFKA_REPLICATION_FACTOR", "1"))
    
    # Database Configuration
    db_host: str = os.getenv("DB_HOST", "postgres")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "ong_management")
    db_user: str = os.getenv("DB_USER", "ong_user")
    db_password: str = os.getenv("DB_PASSWORD", "ong_pass")
    
    # Service Configuration
    service_port: int = int(os.getenv("SERVICE_PORT", "50054"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def kafka_bootstrap_servers(self) -> List[str]:
        return self.kafka_brokers.split(",")
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"


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