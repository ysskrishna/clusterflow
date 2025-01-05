from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.routers.user import router as user_router
from src.routers.organization import router as organization_router
from src.routers.cluster import router as cluster_router
from src.routers.deployment import router as deployment_router
from src.seed import add_seed_data_if_empty, drop_all_tables, create_tables_if_not_exists

app = FastAPI()

app.include_router(user_router, prefix="/api/user", tags=["user"])
app.include_router(organization_router, prefix="/api/organization", tags=["organization"])
app.include_router(cluster_router, prefix="/api/cluster", tags=["cluster"])
app.include_router(deployment_router, prefix="/api/deployment", tags=["deployment"])


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return """
    <html>
    <head>
        <title>Clusterflow</title>
    </head>
    <body>
        <h1>Clusterflow API</h1>
    </body>
    </html>
    """

# Create Database Tables
@app.on_event("startup")
async def init_db():
    drop_tables = False # Make it true to drop all tables. It will reset the database with initial data

    if drop_tables:
        await drop_all_tables()

    # Create all tables if they don't exist
    await create_tables_if_not_exists()

    # Seed the database if database is empty
    await add_seed_data_if_empty()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8081)