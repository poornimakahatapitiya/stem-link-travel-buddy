from fastapi import FastAPI
from src.main.controller.v1 import generic_agent_router

app = FastAPI(
    title="app",
    description="API that helps configure .",
    version="1.0.0",
    root_path="/api",
)



app.include_router(generic_agent_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "travel-buddy-app"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "travel-buddy API", "version": "1.0.0"}
