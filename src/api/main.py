from fastapi import FastAPI

from src.api.routers import health

app = FastAPI(
    title="Nifty100 Financial Analysis API",
    version="1.0.0",
    description="REST API for financial analytics and stock screening."
)

app.include_router(health.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Nifty100 Financial Analysis API"
    }