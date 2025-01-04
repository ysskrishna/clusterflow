from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.routers.user import router as user_router
from src.routers.organization import router as organization_router
from src.routers.cluster import router as cluster_router

from src.core.dbutils import engine, Base


app = FastAPI()

app.include_router(user_router, prefix="/api/user", tags=["user authentication"])
app.include_router(organization_router, prefix="/api/organization", tags=["organization"])
app.include_router(cluster_router, prefix="/api/cluster", tags=["cluster"])


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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8081)