from fastapi import FastAPI
from app.modules.auth.router import router as auth_router
from app.modules.catalog.router import router as catalog_router
from app.modules.inventory.router import router as inventory_router
from app.modules.sales.router import router as sales_router
from app.modules.logistics.router import router as logistics_router

app = FastAPI(
    title="Tecno Rev API",
    description="API for Tecno Rev e-commerce platform",
    version="1.0.0"
)

# Include routers
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(inventory_router)
app.include_router(sales_router)
app.include_router(logistics_router)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Tecno Rev API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "modules": [
            "Authentication (/api/auth)",
            "Catalog (/api/catalog)",
            "Inventory (/api/inventory)",
            "Sales (/api/sales)",
            "Logistics (/api/logistics)"
        ]
    }
