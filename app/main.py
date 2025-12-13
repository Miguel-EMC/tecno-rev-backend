from fastapi import FastAPI
from app.modules.auth.router import router as auth_router

app = FastAPI(
    title="Tecno Rev API",
    description="API for Tecno Rev e-commerce platform",
    version="1.0.0"
)

# Include routers
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Tecno Rev API", "status": "running"}
