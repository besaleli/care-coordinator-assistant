"""ML services."""
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def index():
    """Homepage"""
    return 'API is up and running!'
