"""ML services."""
from fastapi import FastAPI
from .models import Patient
from .routers.message import router as message_router

app = FastAPI()

app.include_router(
    message_router,
    prefix='/message',
    tags=['message']
    )

@app.get('/')
async def index():
    """Homepage"""
    return 'ML services are up and running! <3'

@app.get('/debug/user')
def patient():
    return Patient.get_by_id(1).model_dump()
