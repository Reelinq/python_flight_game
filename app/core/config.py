from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    initial_co2_budget: float = Field(default=2000, alias="INITIAL_CO2_BUDGET")
    co2_per_100km: float = Field(default=20, alias="CO2_PER_100KM")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
