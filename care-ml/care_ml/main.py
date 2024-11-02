"""ML services."""
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def index():
    """Homepage"""
    return 'ML services are up and running! <3'

@app.post('/message')
async def message():
    return "This is a message!"
