from fastapi import FastAPI

app = FastAPI(
    title="Mini CRM - Lead Distribution System",
    description="Система распределения лидов между операторами по источникам",
    version="1.0.0"
)


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
