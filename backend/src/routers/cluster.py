from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.dbutils import get_db
from src.core.jwtutils import get_current_user
from src.models import schemas
from src.models.models import User, UserOrganization, Cluster

router = APIRouter()


@router.post("/create")
async def create_cluster(cluster: schemas.ClusterCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # check if user is in the organization
    result = await db.execute(select(UserOrganization).where(UserOrganization.user_id == user.user_id, UserOrganization.organization_id == cluster.organization_id))
    user_org = result.scalar_one_or_none()
    if not user_org:
        raise HTTPException(status_code=403, detail="User not in organization")
    
    new_cluster = Cluster(
        name=cluster.name,
        total_ram=cluster.total_ram,
        total_cpu=cluster.total_cpu,
        total_gpu=cluster.total_gpu,
        available_ram=cluster.total_ram,
        available_cpu=cluster.total_cpu,
        available_gpu=cluster.total_gpu,
        organization_id=cluster.organization_id,
        user_id=user.user_id
    )
    db.add(new_cluster)
    await db.commit()
    await db.refresh(new_cluster)
    return new_cluster

@router.get("/{cluster_id}")
async def get_cluster(cluster_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Cluster).where(Cluster.cluster_id == cluster_id))
    cluster = result.scalar_one_or_none()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # check if user is in the organization
    result = await db.execute(select(UserOrganization).where(UserOrganization.user_id == user.user_id, UserOrganization.organization_id == cluster.organization_id))
    user_org = result.scalar_one_or_none()
    if not user_org:
        raise HTTPException(status_code=403, detail="User does not have access to this cluster")
    
    return cluster
