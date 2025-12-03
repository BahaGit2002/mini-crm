from fastapi import FastAPI

from app.routes import operators, sources, appeals, stats

app = FastAPI(
    title="Mini CRM - Lead Distribution System",
    description="A system for distributing leads between operators by source",
    version="1.0.0"
)

app.include_router(operators.router)
app.include_router(sources.router)
app.include_router(appeals.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {
        "message": "Mini CRM API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
