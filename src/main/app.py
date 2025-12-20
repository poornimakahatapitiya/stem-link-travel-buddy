from contextlib import asynccontextmanager

# Initialize Datadog BEFORE importing FastAPI
from src.main.config.datadog_config import init_datadog, DatadogConfig
init_datadog()

# Now import FastAPI
from fastapi import FastAPI
from src.main.controller.v1 import generic_agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    DatadogConfig.shutdown()


app = FastAPI(
    title="app",
    description="API that helps configure .",
    version="1.0.0",
    root_path="/api",
    lifespan=lifespan
)


app.include_router(prefix="/v1",router=generic_agent_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "travel-buddy-app"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "travel-buddy API", "version": "1.0.0"}
