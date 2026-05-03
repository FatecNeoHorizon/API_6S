from pathlib import Path
from typing import Optional
import logging
import os

from dotenv import load_dotenv
from pydantic import ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _load_env_files():
    """Load .env files from envs/ directory based on APP_ENV."""
    app_env = os.getenv("APP_ENV", "dev")
    settings_file = Path(__file__).resolve()

    for parent in settings_file.parents:
        envs_dir = parent / "envs"

        if not envs_dir.exists():
            continue

        loaded_any = False

        for env_file in (
            envs_dir / f".env.backend.{app_env}",
            envs_dir / ".env.backend",
            envs_dir / f".env.postgres.{app_env}",
            envs_dir / ".env.postgres",
            envs_dir / f".env.mongo.{app_env}",
            envs_dir / ".env.mongo",
        ):
            if env_file.exists():
                load_dotenv(dotenv_path=str(env_file), override=False)
                loaded_any = True

        if loaded_any:
            return


_load_env_files()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_env: str = Field(default="dev")
    backend_url: Optional[str] = Field(default=None)
    frontend_url: Optional[str] = Field(default=None)

    # File Upload Settings
    csv_file_path: str = Field(default="/app/data/indicadores-continuidade-coletivos-2020-2029.csv")
    max_upload_size_mb: int = Field(default=500)
    tmp_upload_path: str = Field(default="tmp/uploads")

    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    postgres_db: str = Field(default="postgres")
    postgres_sslmode: str = Field(default="prefer")

    mongo_host: str = Field(default="mongo_db")
    mongo_port: int = Field(default=27017)
    mongo_user: str = Field(default="")
    mongo_password: str = Field(default="")
    mongo_db_name: str = Field(default="tecsys")

    mongo_max_pool_size: int = Field(default=10)
    mongo_server_selection_timeout_ms: int = Field(default=120000)
    mongo_connect_timeout_ms: int = Field(default=10000)

    # Model retraining policy
    model_retrain_on_new_data: bool = Field(default=False)
    model_retrain_strategy: str = Field(default="per_load")
    model_retrain_min_new_records: int = Field(default=1)

    # PostgreSQL Configuration
    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    postgres_db: str = Field(default="postgres")
    postgres_sslmode: str = Field(default="prefer")

    # User Security Configuration
    email_hash_salt: str = Field(default="change-me")
    email_encryption_key: Optional[str] = Field(default=None)

    jwt_secret_key: str = Field(default="change-this-jwt-secret-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=60)

    model_config = ConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_mongo_credentials(self) -> "Settings":
        if not self.mongo_user:
            self.mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME", "")

        if not self.mongo_password:
            self.mongo_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "")

        if not self.mongo_user or not self.mongo_password:
            raise ValueError(
                "MongoDB credentials are missing. "
                "Set MONGO_USER/MONGO_PASSWORD or MONGO_INITDB_ROOT_USERNAME/MONGO_INITDB_ROOT_PASSWORD."
            )

        return self

    @property
    def mongo_uri(self) -> str:
        return (
            f"mongodb://{self.mongo_user}:{self.mongo_password}@"
            f"{self.mongo_host}:{self.mongo_port}/{self.mongo_db_name}?"
            f"authSource=admin"
        )

    @property
    def postgres_dsn(self) -> str:
        return (
            f"host={self.postgres_host} "
            f"port={self.postgres_port} "
            f"user={self.postgres_user} "
            f"password={self.postgres_password} "
            f"dbname={self.postgres_db}"
        )