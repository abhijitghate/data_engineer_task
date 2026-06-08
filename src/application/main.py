from fastapi import FastAPI

from src.application.routers import companies, pipeline_runs, snapshots, uploads

app = FastAPI(
    title="Corporate Credit Rating API",
    version="0.1.0",
    description="Read-focused API for corporate rating warehouse data.",
)

app.include_router(companies.router)
app.include_router(snapshots.router)
app.include_router(uploads.router)
app.include_router(pipeline_runs.router)


@app.get("/health", tags=["health"])
def healthcheck():
    return {"status": "ok"}
