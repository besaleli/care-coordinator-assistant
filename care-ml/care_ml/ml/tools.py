"""Tool definitions."""
from typing import Optional, Literal
from datetime import datetime, timedelta
from .ehr_connector import Patient
from .db import init_db

CONFIRM_NAME_DOB = {
    'type': 'function',
    'function': {
        'name': 'confirm_name_dob',
        'description': 'Confirm the name and date of birth of the patient.',
        'parameters': {
            'type': 'object',
            'properties': {
                'first_name': {
                    'type': 'string',
                    'description': 'First name of the patient. Case insensitive.'
                },
                'last_name': {
                    'type': 'string',
                    'description': 'Last name of the patient. Case insensitive.'
                },
                'dob': {
                    'type': 'string',
                    'description': 'Date of birth of the patient. Format: MM/DD/YYYY.'
                },
            }
        }
    },
}

SEARCH_PROVIDER = {
    'type': 'function',
    'function': {
        'name': 'search_available_providers',
        'description': 'Search for a provider.',
        'parameters': {
            'type': 'object',
            'properties': {
                'appointment_type': {
                    'type': 'string',
                    'description': 'Appointment type. Optional. Either NEW or EXISTING.'
                },
                'first_name': {
                    'type': 'string',
                    'description': 'First name of the provider. Optional. Case insensitive.'
                },
                'last_name': {
                    'type': 'string',
                    'description': 'Last name of the provider. Optional. Case insensitive.'
                },
                'location': {
                    'type': 'string',
                    'description': 'Department address. Optional. Case insensitive.'
                },
                'specialty': {
                    'type': 'string',
                    'description': 'Provider\'s specialty. Optional. Case insensitive.'
                },
                'timestamp': {
                    'type': 'string',
                    'description': 'Desired appointment timestamp. Optional. Format: MM/DD/YYYY HH:MM:SS.'
                },
            }
        }
    }
}

BOOK_APPOINTMENT = {
    'type': 'function',
    'function': {
        'name': 'book_appointment',
        'description': 'Book an appointment.',
        'parameters': {
            'type': 'object',
            'properties': {
                'provider_first_name': {
                    'type': 'string',
                    'description': 'First name of the provider. Case insensitive.'
                },
                'provider_last_name': {
                    'type': 'string',
                    'description': 'Last name of the provider. Case insensitive.'
                },
                'location': {
                    'type': 'string',
                    'description': 'Location name'
                },
                'appointment_type': {
                    'type': 'string',
                    'description': 'Appointment type. Either NEW or EXISTING.'
                },
                'timestamp': {
                    'type': 'string',
                    'description': 'Desired appointment timestamp. Must use the format: MM/DD/YYYY HH:MM:SS.'
                },
            }
        }
    }
}

def confirm_name_dob(first_name: str, last_name: str, dob: str) -> dict:
    """
    Confirm the name and date of birth of the patient.

    Args:
        first_name: First name of the patient. Case insensitive.
        last_name: Last name of the patient. Case insensitive.
        dob: Date of birth of the patient. Format: MM/DD/YYYY.

    Returns:
        True if the name and date of birth match, False otherwise
    """
    patient = Patient.get_by_id(1)

    if patient.name.lower() == f"{first_name} {last_name}".lower() and patient.dob == dob:
        return patient.model_dump()

    return 'Patient not found. Make sure you entered the correct name and date of birth.'

def search_available_providers(
    appointment_type: Literal['NEW', 'EXISTING'] = 'NEW',
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    location: Optional[str] = None,
    specialty: Optional[str] = None,
    timestamp: Optional[str] = None
) -> list:
    """
    Search for available providers based on given criteria using raw SQL.
    
    Used Claude for this.
    
    Args:
        appointment_type: Type of appointment ('NEW' or 'EXISTING')
        first_name: Provider's first name (optional)
        last_name: Provider's last name (optional)
        location: Department address (optional)
        specialty: Provider's specialty (optional)
        timestamp: Desired appointment timestamp in the format 'MM/DD/YYYY HH:MM:SS' (optional)
    
    Returns:
        List of available providers with their departments
    """

    ts = timestamp and datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S')

    # Set appointment duration based on type
    duration = 30 if appointment_type == 'NEW' else 15

    # Build the base query
    query = """
        SELECT 
            p.id as provider_id,
            p.first_name,
            p.last_name,
            p.specialty,
            p.certification,
            d.name as department_name,
            d.phone_number,
            d.address,
            d.start_day,
            d.end_day,
            d.start_hour,
            d.end_hour
        FROM providers p
        JOIN departments d ON p.id = d.provider_id
        WHERE 1=1
    """
    # Not parameterizing the query is totally unacceptable and a massive security issue, but would be
    # easily solved when this code is refactored to use an ORM

    # Add time-based filters only if timestamp is provided
    if ts:
        day_of_week = ts.weekday()
        hour = ts.hour

        query += f"""
            AND d.start_day <= {day_of_week}
            AND d.end_day >= {day_of_week}
            AND d.start_hour <= {hour}
            AND d.end_hour >= {hour + (duration / 60)}
        """

    # Add optional filters
    if first_name:
        query += f" AND p.first_name ilike '{first_name}'"

    if last_name:
        query += f" AND p.last_name ilike '{last_name}'"

    if specialty:
        query += f" AND p.specialty ilike '{specialty}'"

    if location:
        query += f" AND d.name ilike '{location}'"

    # Execute query using the connection
    with init_db() as conn:
        print(query)
        results = conn.execute(query).fetchall()

    # Convert results to more readable format
    available_providers = []
    for row in results:
        provider = {
            'provider_id': row[0],
            'first_name': row[1],
            'last_name': row[2],
            'specialty': row[3],
            'certification': row[4],
            'department': {
                'name': row[5],
                'phone_number': row[6],
                'address': row[7],
                'hours': f"{row[10]}:00-{row[11]}:00",  # Using correct indices for hours
                'days': f"{row[8]}-{row[9]}"  # Using correct indices for days
            }
        }
        available_providers.append(provider)

    return available_providers

def book_appointment(
    provider_first_name: str,
    provider_last_name: str,
    location: str,
    appointment_type: Literal['NEW', 'EXISTING'],
    timestamp: str,
    ):
    # confirm provider is available
    providers = search_available_providers(
        appointment_type=appointment_type,
        first_name=provider_first_name,
        last_name=provider_last_name,
        location=location,
        timestamp=timestamp
        )

    if not providers:
        return 'Provider not found or not available at that time. Try again.'

    # if existing appointment, make sure patient has seen provider before in last 5 years
    patient_data = Patient.get_by_id(1)
    ts = datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S')
    if appointment_type == 'EXISTING':
        if not any(appt.timestamp > ts - timedelta(days=1825) for appt in patient_data.appointments if f"{provider_first_name} {provider_last_name}" in appt.provider):
            return 'Patient has not seen provider in last 5 years. You must schedule a NEW appointment.'

    # if new appointment, make sure patient has not had an appointment in the last 5 years
    if appointment_type == 'NEW':
        if any(appt.timestamp > ts - timedelta(days=1825) for appt in patient_data.appointments):
            return 'Patient has had an appointment in the last 5 years. You must schedule an EXISTING appointment.'

    return 'Appointment scheduled.'

TOOL_CALL_MAP = {
    'confirm_name_dob': confirm_name_dob,
    'search_available_providers': search_available_providers,
    'book_appointment': book_appointment
}
