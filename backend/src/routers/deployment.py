from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.dbutils import get_db
from src.core.jwtutils import get_current_user
from src.models import schemas
from src.models.models import User, UserOrganization, Cluster, Deployment
from src.models.enums import DeploymentStatus
from src.core.redisutils import add_deployment_to_queue 

router = APIRouter()

@router.post("/create")
async def create_deployment(deployment: schemas.DeploymentCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # check if cluster exists
    cluster = await db.get(Cluster, deployment.cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # check if user is in the cluster organization
    result = await db.execute(select(UserOrganization).where(UserOrganization.user_id == user.user_id, UserOrganization.organization_id == cluster.organization_id))
    user_org = result.scalar_one_or_none()
    if not user_org:
        raise HTTPException(status_code=403, detail="User does not have access to this cluster")
    

    new_deployment = Deployment(
        cluster_id=deployment.cluster_id,
        organization_id=cluster.organization_id,
        user_id=user.user_id,
        docker_image_path=deployment.docker_image_path,
        required_ram=deployment.required_ram,
        required_cpu=deployment.required_cpu,
        required_gpu=deployment.required_gpu,
        priority=deployment.priority,
        status=DeploymentStatus.QUEUED
    )

    db.add(new_deployment)
    await db.commit()
    await db.refresh(new_deployment)

    # Add deployment to Redis queue
    add_deployment_to_queue(new_deployment.cluster_id, new_deployment.deployment_id, new_deployment.priority)
    
    return {"message": f"Deployment {new_deployment.deployment_id} added to the queue"}
