from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.routers.user import router as user_router
from src.routers.organization import router as organization_router
from src.routers.cluster import router as cluster_router
from src.routers.deployments import router as deployments_router
from src.core.dbutils import engine, Base
from src.seed import seed_data

app = FastAPI()

app.include_router(user_router, prefix="/api/user", tags=["user"])
app.include_router(organization_router, prefix="/api/organization", tags=["organization"])
app.include_router(cluster_router, prefix="/api/cluster", tags=["cluster"])
app.include_router(deployments_router, prefix="/api/deployments", tags=["deployments"])


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
    drop_tables = False # Make it true to drop all tables and reset the database with initial data

    if drop_tables:
        # Drop all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("#########################")
        print("All tables dropped.")
        print("#########################")

    # Create all tables if it doesn't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed the database if database is empty
    await seed_data()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8081)