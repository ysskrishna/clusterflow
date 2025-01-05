from src.core.passwordutils import get_password_hash
from src.models.models import User, Organization, UserOrganization, Cluster, Deployment
from src.models.enums import UserOrganizationRole
from src.core.dbutils import SessionLocal
from sqlalchemy.sql import text
from src.core.dbutils import engine, Base


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
            total_ram=16,
            total_cpu=8,
            total_gpu=4,
            available_ram=16,
            available_cpu=8,
            available_gpu=4,
            organization_id=org1.organization_id,
            user_id=user1.user_id
        )
        print(f"Created cluster with name: {cluster1.name}, available ram: {cluster1.available_ram}, available cpu: {cluster1.available_cpu}, available gpu: {cluster1.available_gpu}")
        db.add(cluster1)
        await db.commit()

        print("#########################")
        print("Seed data added successfully.")
        print("#########################")

