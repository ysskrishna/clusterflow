import asyncio
from datetime import datetime
from src.core.dbutils import SessionLocal
from src.models.models import Cluster, Deployment
from src.core.config import Config
from sqlalchemy.future import select
from src.core.redisutils import redis_client, get_cluster_queue_name, delete_deployment_from_queue
from src.models.enums import DeploymentStatus
import json



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

async def schedule_cluster_deployments():
    print("#########################")
    print("Starting scheduler")
    print("#########################")
    
    db = SessionLocal()

    while True:
        result = await db.execute(select(Cluster))
        clusters = result.scalars().all()

        for cluster in clusters:
            print(f"{datetime.now()} - Scheduling deployments for cluster_id {cluster.cluster_id}, with cluster name {cluster.name}")

            cluster_queue_name = get_cluster_queue_name(cluster.cluster_id)

            # Fetch deployments for this cluster, sorted by priority (highest priority first)
            queued_deployments = redis_client.zrevrange(cluster_queue_name, 0, 0, withscores=True)

            if not queued_deployments:
                continue  # No deployments for this cluster to process

            # Parse deployment data and priority
            deployment_data, priority = queued_deployments[0]
            deployment_info = json.loads(deployment_data)
            deployment_id = deployment_info.get("deployment_id")

            # Fetch deployment details from database
            result = await db.execute(select(Deployment).filter(Deployment.deployment_id == deployment_id))
            deployment = result.scalar_one_or_none()

            # If the deployment is invalid or doesn't belong to the current cluster, skip it
            if not deployment or deployment.cluster_id != cluster.cluster_id:
                delete_deployment_from_queue(cluster.cluster_id, deployment_data)  # Clean invalid entry
                continue

            if has_sufficient_resources(cluster, deployment):
                await allocate_resources(cluster, deployment, db)

                # Remove the deployment from the queue
                delete_deployment_from_queue(cluster.cluster_id, deployment_data)

                # Log successful scheduling
                print(f"Deployment {deployment_id} scheduled on cluster {cluster.name}")
            else:
                # Log if resources are insufficient (deployment remains in the queue)
                print(f"Deployment {deployment_id} queued due to insufficient resources")

        await asyncio.sleep(Config.SCHEDULER_RETRY_INTERVAL)



