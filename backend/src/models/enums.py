from enum import Enum


class UserOrganizationRole(int, Enum):
    OWNER = 1
    MEMBER = 2

class DeploymentStatus(int, Enum):
    QUEUED = 1
    RUNNING = 2