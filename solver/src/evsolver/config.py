from pydantic import BaseModel
import os

class Settings(BaseModel):
    log_level: str = os.getenv("EVSOLVER_LOG_LEVEL", "INFO")
    time_limit_seconds: int = int(os.getenv("EVSOLVER_TIME_LIMIT_S", "10"))
    max_repairs_per_route: int = int(os.getenv("EVSOLVER_MAX_REPAIRS", "8"))

settings = Settings()