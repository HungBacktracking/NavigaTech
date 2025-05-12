from fastapi import APIRouter

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.user import router as user_router
from app.api.endpoints.job import router as job_router
from app.api.endpoints.job_task import router as job_task_router
from app.api.endpoints.ws import router as ws_router
from app.api.endpoints.chat import router as chat_router
from app.api.endpoints.resume import router as resume_router

routers = APIRouter()
router_list = [auth_router, user_router, job_router, job_task_router, ws_router, chat_router, resume_router]

for router in router_list:
    router.tags = routers
    routers.include_router(router)
