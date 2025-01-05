from redis import Redis
from src.core.config import Config
import json
redis_client = Redis(host=Config.REDIS_HOST, port= Config.REDIS_PORT, decode_responses=True)


def get_cluster_queue_name(cluster_id: int):
    return f"{Config.REDIS_CLUSTER_QUEUE_PREFIX}{cluster_id}"

def add_deployment_to_queue(cluster_id: int, deployment_id: int, priority: int):
    queue_name = get_cluster_queue_name(cluster_id)
    redis_client.zadd(queue_name, {json.dumps({"deployment_id": deployment_id, "priority": priority}): priority})

def delete_deployment_from_queue(cluster_id: int, data: str):
    queue_name = get_cluster_queue_name(cluster_id)
    redis_client.zrem(queue_name, data)


