"""EHR System Connector."""
from typing import List, Optional
import logging
import re
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

def convert_to_timestamp(date_str: str, time_str: str) -> datetime:
    """
    Convert date string (MM/DD/YY) and time string (H:MMam/pm) to a timestamp.
    
    Args:
        date_str (str): Date in format "MM/DD/YY"
        time_str (str): Time in format "H:MMam" or "H:MMpm"
    
    Returns:
        datetime: Timestamp object
    
    Raises:
        ValueError: If date or time format is invalid
    """
    # Validate date format
    if not re.match(r'^\d{1,2}/\d{1,2}/\d{2}$', date_str):
        raise ValueError("Date must be in format MM/DD/YY")
    
    # Validate time format
    if not re.match(r'^\d{1,2}:\d{2}[ap]m$', time_str.lower()):
        raise ValueError("Time must be in format H:MMam or H:MMpm")
    
    # Parse date components
    month, day, year = map(int, date_str.split('/'))
    year = 2000 + year if year < 100 else year  # Convert 2-digit year to 4-digit
    
    # Parse time components
    time_str = time_str.lower()
    hour, minute = time_str[:-2].split(':')
    hour = int(hour)
    minute = int(minute)
    
    # Adjust hour for PM
    if 'pm' in time_str and hour != 12:
        hour += 12
    elif 'am' in time_str and hour == 12:
        hour = 0
        
    return datetime(year, month, day, hour, minute)

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

    @property
    def timestamp(self) -> datetime:
        """Parse date and time and return a datetime object. Used Claude for this."""
        # Validate date format
        date_str = self.date
        time_str = self.time
        if not re.match(r'^\d{1,2}/\d{1,2}/\d{2}$', date_str):
            raise ValueError("Date must be in format MM/DD/YY")

        # Validate time format
        if not re.match(r'^\d{1,2}:\d{2}[ap]m$', time_str.lower()):
            raise ValueError("Time must be in format H:MMam or H:MMpm")

        # Parse date components
        month, day, year = map(int, date_str.split('/'))
        year = 2000 + year if year < 100 else year  # Convert 2-digit year to 4-digit

        # Parse time components
        time_str = time_str.lower()
        hour, minute = time_str[:-2].split(':')
        hour = int(hour)
        minute = int(minute)

        # Adjust hour for PM
        if 'pm' in time_str and hour != 12:
            hour += 12
        elif 'am' in time_str and hour == 12:
            hour = 0

        return datetime(year, month, day, hour, minute)


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
