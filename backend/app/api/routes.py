from fastapi import APIRouter

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.user import router as user_router
from app.api.endpoints.job import router as job_router

routers = APIRouter()
router_list = [auth_router, user_router, job_router]

for router in router_list:
    router.tags = routers
    routers.include_router(router)
