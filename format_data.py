"""Throw data into a duckdb instance"""
import pandas as pd
import duckdb

providers = [
    {
        "id": 1,
        "first_name": "Meredith",
        "last_name": "Grey",
        "specialty": "Primary Care",
        "certification": "MD",
    },
    {
        "id": 2,
        "first_name": "Gregory",
        "last_name": "House",
        "specialty": "Orthopedics",
        "certification": "MD",
    },
    {
        "id": 3,
        "first_name": "Cristina",
        "last_name": "Yang",
        "specialty": "Surgery",
        "certification": "MD",
    },
    {
        "id": 4,
        "first_name": "Chris",
        "last_name": "Perry",
        "specialty": "Primary Care",
        "certification": "FNP",
    },
    {
        "id": 5,
        "first_name": "Temperance",
        "last_name": "Brennan",
        "specialty": "Orthopedics",
        "certification": "PhD, MD",
    }
]

departments = [
    {
        "id": 1,
        "provider_id" : 1,
        "name": "Sloan Primary Care",
        "phone_number": "(710) 555-2070",
        "address": "202 Maple St, Winston-Salem, NC 27101",
        "start_day": 0,
        "end_day": 4,
        "start_hour": 9,
        "end_hour": 17
    },
    {
        "id": 2,
        "provider_id" : 2,
        "name": "PPTH Orthopedics",
        "phone_number": "(445) 555-6205",
        "address": "101 Pine St, Greensboro, NC 27401",
        "start_day": 0,
        "end_day": 2,
        "start_hour": 9,
        "end_hour": 17
    },
    {
        "id": 3,
        "provider_id" : 2,
        "name": "Jefferson Hospital",
        "phone_number": "(215) 555-6123",
        "address": "202 Maple St, Claremont, NC 28610",
        "start_day": 3,
        "end_day": 4,
        "start_hour": 9,
        "end_hour": 17
    },
    {
        "id": 4,
        "provider_id" : 3,
        "name": "Seattle Grace Cardiac Surgery",
        "phone_number": "(710) 555-3082",
        "address": "456 Elm St, Charlotte, NC 28202",
        "start_day": 0,
        "end_day": 4,
        "start_hour": 9,
        "end_hour": 17
    },
    {
        "id": 5,
        "provider_id" : 4,
        "name": "Sacred Heart Surgical Department",
        "phone_number": "(339) 555-7480",
        "address": "123 Main St, Raleigh, NC 27601",
        "start_day": 0,
        "end_day": 2,
        "start_hour": 9,
        "end_hour": 17
    },
    {
        "id": 6,
        "provider_id" : 5,
        "name": "Jefferson Hospital",
        "phone_number": "(215) 555-6123",
        "address": "202 Maple St, Claremont, NC 28610",
        "start_day": 1,
        "end_day": 3,
        "start_hour": 10,
        "end_hour": 16
    }
]

providers = pd.DataFrame(providers)
departments = pd.DataFrame(departments)

with duckdb.connect('data/providers.db') as conn:
    conn.execute("CREATE OR REPLACE TABLE providers AS SELECT * FROM providers")
    conn.execute("CREATE OR REPLACE TABLE departments AS SELECT * FROM departments")
    conn.commit()

    assert len(conn.execute("SELECT * FROM providers").fetchall()) == 5
    assert len(conn.execute("SELECT * FROM departments").fetchall()) == 6
