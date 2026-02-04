from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Odoo
    odoo_url: str | None = Field(default=None, validation_alias="ODOO_URL")
    odoo_db: str | None = Field(default=None, validation_alias="ODOO_DB")
    odoo_user: str | None = Field(default=None, validation_alias="ODOO_USER")
    odoo_password: str | None = Field(default=None, validation_alias="ODOO_PASSWORD")

    # Sécurité
    jwt_secret: str = Field(default="change-me-jwt", validation_alias="JWT_SECRET")
    jwt_expire_minutes: int = Field(default=60, validation_alias="JWT_EXPIRE_MINUTES")
    hmac_secret: str = Field(default="change-me-hmac", validation_alias="HMAC_SECRET")

    # Auth de démo (login /auth/login)
    admin_username: str = Field(default="admin", validation_alias="ADMIN_USERNAME")
    admin_password: str = Field(default="admin", validation_alias="ADMIN_PASSWORD")

    # Base de données
    database_url: str = Field(
        default="sqlite:///./contacts.db", validation_alias="DATABASE_URL"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
    )


settings = Settings()

