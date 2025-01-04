from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class OrganizationCreate(BaseModel):
    name: str

class OrganizationJoin(BaseModel):
    invite_code: str
