from fastapi import APIRouter
from app.api.v1.endpoints import agent_endpoints

api_router = APIRouter()
api_router.include_router(agent_endpoints.router, tags=["AutoPersona Engine"])
