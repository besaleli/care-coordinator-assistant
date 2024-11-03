"""EHR System Connector."""
from typing import List, Optional
import logging
from datetime import datetime, time, timedelta
from enum import StrEnum
import requests
from pydantic import BaseModel, Field
from ..env_settings import API_URL

logger = logging.getLogger(__name__)

def subtract_minutes_from_time(t: time, minutes: int) -> time:
    """Subtract minutes from time."""
    dt = datetime.combine(datetime.min, t) - timedelta(minutes=minutes)

    return dt.time()

class Status(StrEnum):
    """Appointment status."""
    BOOKED = "booked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NOSHOW = "noshow"


class AppointmentType(StrEnum):
    """Appointment type."""
    NEW = "NEW"
    ESTABLISHED = "ESTABLISHED"

class Referral(BaseModel):
    """Referral."""
    provider: Optional[str] = None
    specialty: str


class Appointment(BaseModel):
    """Appointment."""
    date: str
    time: str
    provider: str
    status: str


class Patient(BaseModel):
    """Patient."""
    id: int
    name: str
    dob: str
    pcp: str
    ehr_id: str = Field(alias="ehrId")
    referred_providers: List[Referral]
    appointments: List[Appointment]

    @classmethod
    def get_by_id(cls, idx: int) -> 'Patient':
        """Get patient by ID

        Args:
            idx (int): Patient ID

        Raises:
            err: HTTPError if request fails

        Returns:
            Patient: Patient object
        """
        response = requests.get(
            f"{API_URL}/patient/{idx}",
            timeout=30,
            )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(
                "[%s] %s",
                response.status_code,
                response.text
                )
            raise err

        return cls(**response.json())
