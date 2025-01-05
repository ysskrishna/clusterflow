from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.dbutils import get_db
from src.core.jwtutils import get_current_user
from src.models import schemas
from src.models.models import User, UserOrganization, Cluster, Deployment

router = APIRouter()

@router.post("/create")
async def create_deployment(deployment: schemas.DeploymentCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pass
