from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.api.routes import routers
from app.core.config import configs
from app.core.containers.application_container import ApplicationContainer
from app.exceptions.exception_handlers import register_exception_handlers
from app.util.class_object import singleton


@singleton
class AppCreator:
    def __init__(self):
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.container.init_resources()
            # self.db.create_database()
            await self.mongo.init_mongo()
            yield
            # Shutdown
            self.container.shutdown_resources()

        # set app default
        self.app = FastAPI(
            title=configs.PROJECT_NAME,
            openapi_url=f"{configs.API}/openapi.json",
            version="0.0.1",
            lifespan=lifespan,
        )
        register_exception_handlers(self.app)

        # set db and container
        self.container = ApplicationContainer()

        self.db = self.container.database().db()
        self.mongo = self.container.database().mongo_db()

        # set cors
        if configs.BACKEND_CORS_ORIGINS:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in configs.BACKEND_CORS_ORIGINS],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        # set routes
        @self.app.get("/", include_in_schema=False)
        def health() -> JSONResponse:
            return JSONResponse({"message": "Server is working!"})

        self.app.include_router(routers, prefix=configs.API_V1_STR)



app_creator = AppCreator()
app = app_creator.app
db = app_creator.db
container = app_creator.container
