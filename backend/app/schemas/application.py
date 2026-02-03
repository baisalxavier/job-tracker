from enum import Enum
from pydantic import BaseModel, Field
from pydantic import ConfigDict


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"


class ApplicationCreate(BaseModel):
    company: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., min_length=2, max_length=100)
    status: ApplicationStatus = ApplicationStatus.APPLIED


class ApplicationOut(ApplicationCreate):
    id: int

    # 🔑 REQUIRED for SQLAlchemy → Pydantic
    model_config = ConfigDict(from_attributes=True)
