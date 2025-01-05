from src.core.passwordutils import get_password_hash
from src.models.models import User, Organization, UserOrganization, Cluster, Deployment
from src.models.enums import UserOrganizationRole
from src.core.dbutils import SessionLocal
from sqlalchemy.sql import text
from src.core.dbutils import engine, Base
from src.models.enums import DeploymentStatus
from src.core.redisutils import add_deployment_to_queue

async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("#########################")
    print("All tables dropped.")
    print("#########################")

async def create_tables_if_not_exists():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def add_seed_data_if_empty():
    async with SessionLocal() as db:
        # Check if there are already users in the database
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        if user_count > 0:
            return  # Skip seeding if data already exists
        
        print("#########################")
        print("Seeding data...")
        print("#########################")

        # Seed Users
        user1 = User(username="user1", password=get_password_hash("pass1234"))
        print(f"Created user with username: {user1.username}")
        user2 = User(username="user2", password=get_password_hash("pass1234"))
        print(f"Created user with username: {user2.username}")
        user3 = User(username="user3", password=get_password_hash("pass1234"))
        print(f"Created user with username: {user3.username}")
        db.add_all([user1, user2, user3])
        await db.commit()

        # Seed Organizations
        org1 = Organization(name="organization1", invite_code="ORG-1-INVITE-CODE")
        print(f"Created organization with name: {org1.name}")
        db.add(org1)
        await db.commit()

        # Refresh users and organization to get the auto-generated IDs
        await db.refresh(user1)
        await db.refresh(user2)
        await db.refresh(user3)
        await db.refresh(org1)
        

        # Seed User-Organization Relations
        user_org1 = UserOrganization(user_id=user1.user_id, organization_id=org1.organization_id, role=UserOrganizationRole.OWNER)  # user1 in org1 owner
        print(f"Added user {user1.username} to organization {org1.name} as owner")
        user_org2 = UserOrganization(user_id=user2.user_id, organization_id=org1.organization_id, role=UserOrganizationRole.MEMBER)  # user2 in org1 member
        print(f"Added user {user2.username} to organization {org1.name} as member")
        db.add_all([user_org1, user_org2])
        await db.commit()

        # Seed Clusters
        cluster1 = Cluster(
            name="cluster1",
            total_ram=8,
            total_cpu=4,
            total_gpu=2,
            available_ram=8,
            available_cpu=4,
            available_gpu=2,
            organization_id=org1.organization_id,
            user_id=user1.user_id
        )
        print(f"Created cluster with name: {cluster1.name}, available ram: {cluster1.available_ram}, available cpu: {cluster1.available_cpu}, available gpu: {cluster1.available_gpu}")
        db.add(cluster1)
        await db.commit()
        await db.refresh(cluster1)


        # Seed Deployments
        deployment1 = Deployment(
            cluster_id=cluster1.cluster_id,
            organization_id=org1.organization_id,
            user_id=user1.user_id,
            docker_image_path="docker_image_path_1",
            required_ram=4,
            required_cpu=2,
            required_gpu=1,
            priority=3,
            status=DeploymentStatus.QUEUED
        )

        deployment2 = Deployment(
            cluster_id=cluster1.cluster_id,
            organization_id=org1.organization_id,
            user_id=user1.user_id,
            docker_image_path="docker_image_path_2",
            required_ram=2,
            required_cpu=1,
            required_gpu=1,
            priority=2,
            status=DeploymentStatus.QUEUED
        )

        deployment3 = Deployment(
            cluster_id=cluster1.cluster_id,
            organization_id=org1.organization_id,
            user_id=user1.user_id,
            docker_image_path="docker_image_path_3",
            required_ram=4,
            required_cpu=2,
            required_gpu=1,
            priority=1,
            status=DeploymentStatus.QUEUED
        )

        db.add_all([deployment1, deployment2, deployment3])
        await db.commit()


        await db.refresh(deployment1)
        await db.refresh(deployment2)
        await db.refresh(deployment3)

        # Add deployments to Redis queue
        add_deployment_to_queue(cluster1.cluster_id, deployment1.deployment_id, deployment1.priority)
        add_deployment_to_queue(cluster1.cluster_id, deployment2.deployment_id, deployment2.priority)
        add_deployment_to_queue(cluster1.cluster_id, deployment3.deployment_id, deployment3.priority)

        print("#########################")
        print("Seed data added successfully.")
        print("#########################")

