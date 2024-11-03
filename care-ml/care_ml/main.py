"""ML services."""
from fastapi import FastAPI
from .routers.message import router as message_router
from .routers.debug import router as debug_router

app = FastAPI()

app.include_router(
    message_router,
    prefix='/message',
    tags=['message']
    )

app.include_router(
    debug_router,
    prefix='/debug',
    tags=['debug']
)

@app.get('/')
async def index():
    """Homepage"""
    return 'ML services are up and running! <3'
