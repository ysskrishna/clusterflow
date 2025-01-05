from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.dbutils import get_db
from src.core.jwtutils import get_current_user
from src.models import schemas
from src.models.models import User, UserOrganization, Cluster, Deployment
from src.models.enums import DeploymentStatus

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
    

    if (deployment.required_ram > cluster.available_ram or
        deployment.required_cpu > cluster.available_cpu or
        deployment.required_gpu > cluster.available_gpu):
        # Insuffienct cluster resources, Queue the deployment
        # await redis_client.rpush("deployments", deployment.json())
        new_deployment = Deployment(
            cluster_id=deployment.cluster_id,
            organization_id=cluster.organization_id,
            user_id=user.user_id,
            docker_image_path=deployment.docker_image_path,
            required_ram=deployment.required_ram,
            required_cpu=deployment.required_cpu,
            required_gpu=deployment.required_gpu,
            priority=deployment.priority,
            status=DeploymentStatus.QUEUED,
            queued_at=datetime.now()
        )
        db.add(new_deployment)
        await db.commit()
        await db.refresh(new_deployment)
        return {"message":"Deployment queued due to insufficient resources", "result":new_deployment}
    else:  

        # Allocate cluster resources
        cluster.available_ram -= deployment.required_ram
        cluster.available_cpu -= deployment.required_cpu
        cluster.available_gpu -= deployment.required_gpu

        new_deployment = Deployment(
            cluster_id=deployment.cluster_id,
            organization_id=cluster.organization_id,
            user_id=user.user_id,
            docker_image_path=deployment.docker_image_path,
            required_ram=deployment.required_ram,
            required_cpu=deployment.required_cpu,
            required_gpu=deployment.required_gpu,
            priority=deployment.priority,
            status=DeploymentStatus.LIVE
        )
        db.add(new_deployment)
        await db.commit()
        await db.refresh(new_deployment)
        return {"message":"Deployment created successfully", "result":new_deployment}



@router.delete("/{deployment_id}/terminate")
async def terminate_deployment(deployment_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    deployment = await db.get(Deployment, deployment_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # check if user is in the cluster organization
    result = await db.execute(select(UserOrganization).where(UserOrganization.user_id == user.user_id, UserOrganization.organization_id == deployment.organization_id))
    user_org = result.scalar_one_or_none()
    if not user_org:
        raise HTTPException(status_code=403, detail="User does not have access to this cluster")

    if deployment.status != DeploymentStatus.LIVE:
        raise HTTPException(status_code=400, detail="Deployment is not live")
    

    cluster = await db.get(Cluster, deployment.cluster_id)

    # Release cluster resources
    cluster.available_ram += deployment.required_ram
    cluster.available_cpu += deployment.required_cpu
    cluster.available_gpu += deployment.required_gpu

    deployment.terminated_at = datetime.now()
    deployment.terminated_by_user_id = user.user_id
    deployment.status = DeploymentStatus.TERMINATED
    await db.commit()
    await db.refresh(deployment)
    return {"message":"Deployment terminated successfully", "result":deployment}



