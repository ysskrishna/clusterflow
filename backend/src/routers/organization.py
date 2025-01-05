import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.dbutils import get_db
from src.core.jwtutils import get_current_user
from src.models import schemas
from src.models.models import User, Organization, UserOrganization
from src.models.enums import UserOrganizationRole

router = APIRouter()

@router.post("/create")
async def create_organization(org: schemas.OrganizationCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    invite_code = f"ORG-{uuid.uuid4()}"
    new_org = Organization(name=org.name, invite_code=invite_code)
    db.add(new_org)
    await db.commit()
    await db.refresh(new_org)
    
    user_org = UserOrganization(user_id=user.user_id, organization_id=new_org.organization_id, role=UserOrganizationRole.OWNER)
    db.add(user_org)
    await db.commit()
    return {"message":"Organization created successfully", "result":new_org}


@router.post("/join")
async def join_organization(org_join: schemas.OrganizationJoin, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization).where(Organization.invite_code == org_join.invite_code))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    
    # check if user is already in the organization
    result = await db.execute(select(UserOrganization).where(UserOrganization.user_id == user.user_id, UserOrganization.organization_id == org.organization_id))
    user_org = result.scalar_one_or_none()
    if user_org:
        raise HTTPException(status_code=400, detail="User already in organization")
    
    user_org = UserOrganization(user_id=user.user_id, organization_id=org.organization_id, role=UserOrganizationRole.MEMBER)
    db.add(user_org)
    await db.commit()
    return {"message":"User joined organization successfully"}


@router.get("/{organization_id}")
async def get_organization(organization_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization).where(Organization.organization_id == organization_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"message":"Organization fetched successfully", "result":org}

@router.get("/{organization_id}/users")
async def get_organization_users(organization_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # check if user is in the organization
    result = await db.execute(select(UserOrganization).where(UserOrganization.user_id == user.user_id, UserOrganization.organization_id == organization_id))
    user_org = result.scalar_one_or_none()
    if not user_org:
        raise HTTPException(status_code=403, detail="User not in organization")
    
    result = await db.execute(select(UserOrganization).where(UserOrganization.organization_id == organization_id))
    users = result.scalars().all()
    return {"message":"Users fetched successfully", "result":users}

