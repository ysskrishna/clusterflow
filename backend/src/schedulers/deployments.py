import asyncio
from datetime import datetime
from src.core.dbutils import SessionLocal
from src.models.models import Cluster, Deployment
from src.core.config import Config
from sqlalchemy.future import select
from src.core.redisutils import redis_client, get_cluster_queue_name, delete_deployment_from_queue, add_deployment_to_queue
from src.models.enums import DeploymentStatus
import json
from typing import List
from sqlalchemy import and_



def has_sufficient_resources(cluster, deployment):
    if cluster.available_cpu >= deployment.required_cpu and cluster.available_ram >= deployment.required_ram and cluster.available_gpu >= deployment.required_gpu:
        return True
    return False

async def allocate_resources(cluster, deployment, db):
    cluster.available_cpu -= deployment.required_cpu
    cluster.available_ram -= deployment.required_ram
    cluster.available_gpu -= deployment.required_gpu
    db.add(cluster)

    deployment.status = DeploymentStatus.RUNNING
    db.add(deployment)
    await db.commit()

async def get_running_deployments(cluster_id: int, db) -> List[Deployment]:
    result = await db.execute(
        select(Deployment)
        .filter(and_(
            Deployment.cluster_id == cluster_id,
            Deployment.status == DeploymentStatus.RUNNING
        ))
        .order_by(Deployment.priority)  # Lower priority first (candidates for preemption)
    )
    return result.scalars().all()

async def preempt_deployments(cluster: Cluster, required_deployment: Deployment, running_deployments: List[Deployment], db) -> bool:
    #Check if we can preempt lower priority deployments to make room for the required deployment.
    
    if required_deployment.priority == 0:  # Don't preempt for lowest priority
        return False
        
    needed_cpu = max(0, required_deployment.required_cpu - cluster.available_cpu)
    needed_ram = max(0, required_deployment.required_ram - cluster.available_ram)
    needed_gpu = max(0, required_deployment.required_gpu - cluster.available_gpu)
    
    freed_cpu, freed_ram, freed_gpu = 0, 0, 0
    to_preempt = []
    
    # Try to find deployments to preempt
    for deployment in running_deployments:
        if deployment.priority >= required_deployment.priority:
            continue  # Don't preempt equal or higher priority deployments
            
        to_preempt.append(deployment)
        freed_cpu += deployment.required_cpu
        freed_ram += deployment.required_ram
        freed_gpu += deployment.required_gpu
        
        if freed_cpu >= needed_cpu and freed_ram >= needed_ram and freed_gpu >= needed_gpu:
            break
    else:
        return False  # Couldn't free enough resources
        
    # Preempt selected deployments
    for deployment in to_preempt:
        # Return resources to cluster
        cluster.available_cpu += deployment.required_cpu
        cluster.available_ram += deployment.required_ram
        cluster.available_gpu += deployment.required_gpu
        
        # Update deployment status
        deployment.status = DeploymentStatus.QUEUED
        db.add(deployment)

        # Re-queue the preempted deployment
        add_deployment_to_queue(cluster.cluster_id, deployment.deployment_id, deployment.priority)
    
    await db.commit()
    return True

async def schedule_cluster_deployments():
    print("#########################")
    print("Starting scheduler")
    print("#########################")
    
    db = SessionLocal()

    while True:
        result = await db.execute(select(Cluster))
        clusters = result.scalars().all()

        for cluster in clusters:
            print(f"{datetime.now()} - Scheduling deployments for cluster_id {cluster.cluster_id}")
            
            cluster_queue_name = get_cluster_queue_name(cluster.cluster_id)
            
            # Get all queued deployments (up to 10) to make better scheduling decisions
            queued_deployments = redis_client.zrevrange(cluster_queue_name, 0, 9, withscores=True)
            if not queued_deployments:
                continue

            for deployment_data, priority in queued_deployments:
                deployment_info = json.loads(deployment_data)
                deployment_id = deployment_info.get("deployment_id")
                
                result = await db.execute(select(Deployment).filter(Deployment.deployment_id == deployment_id))
                deployment = result.scalar_one_or_none()
                
                if not deployment or deployment.cluster_id != cluster.cluster_id:
                    delete_deployment_from_queue(cluster.cluster_id, deployment_data)
                    continue

                if has_sufficient_resources(cluster, deployment):
                    await allocate_resources(cluster, deployment, db)
                    delete_deployment_from_queue(cluster.cluster_id, deployment_data)
                    print(f"Deployment {deployment_id} scheduled on cluster {cluster.name}")
                else:
                    # Try preemption for higher priority deployments
                    running_deployments = await get_running_deployments(cluster.cluster_id, db)
                    if await preempt_deployments(cluster, deployment, running_deployments, db):
                        await allocate_resources(cluster, deployment, db)
                        delete_deployment_from_queue(cluster.cluster_id, deployment_data)
                        print(f"Deployment {deployment_id} scheduled after preemption on cluster {cluster.name}")
                    else:
                        print(f"Deployment {deployment_id} queued due to insufficient resources")

        await asyncio.sleep(Config.SCHEDULER_RETRY_INTERVAL)



