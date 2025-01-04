from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class OrganizationCreate(BaseModel):
    name: str

class OrganizationJoin(BaseModel):
    invite_code: str

class ClusterCreate(BaseModel):
    name: str
    total_ram: int
    total_cpu: int
    total_gpu: int
    organization_id: int