from enum import Enum


class UserOrganizationRole(int, Enum):
    OWNER = 1
    MEMBER = 2

class DeploymentStatus(int, Enum):
    LIVE = 1
    TERMINATED = 2
    QUEUED = 3
