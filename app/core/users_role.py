from enum import Enum




class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    SELLER = "seller"