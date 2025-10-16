"""
Permission and Authorization Utilities
Provides reusable permission checking functions
"""

from typing import List, Union
from app.core.users_role import UserRole
from app.core.error_handlers import AuthorizationError


def check_role_permission(
    current_user: dict,
    allowed_roles: List[Union[UserRole, str]],
    action: str
) -> None:
    """
    Check if user has required role permissions.
    
    Args:
        current_user: Current user dict with 'role' and 'id' keys
        allowed_roles: List of allowed UserRole values or role strings
        action: Description of the action being performed
        
    Raises:
        AuthorizationError: If user doesn't have permission
        
    Example:
        >>> check_role_permission(
        ...     current_user,
        ...     [UserRole.ADMIN, UserRole.SUPERADMIN],
        ...     "view managers"
        ... )
    """
    user_role = current_user.get("role")
    
    if not user_role:
        raise AuthorizationError(
            "User role not found",
            details={"user_id": current_user.get("id")}
        )
    
    # Convert allowed_roles to strings for comparison
    allowed_role_values = []
    for role in allowed_roles:
        if hasattr(role, 'value'):
            allowed_role_values.append(role.value)
        else:
            allowed_role_values.append(str(role))
    
    if user_role not in allowed_role_values:
        raise AuthorizationError(
            f"Insufficient permissions to {action}",
            details={
                "required_roles": allowed_role_values,
                "user_role": user_role,
                "action": action,
                "user_id": current_user.get("id")
            }
        )


def check_user_ownership(
    current_user: dict,
    resource_owner_id: str,
    resource_type: str = "resource"
) -> None:
    """
    Check if the current user owns the resource.
    
    Args:
        current_user: Current user dict
        resource_owner_id: ID of the resource owner
        resource_type: Type of resource for error message
        
    Raises:
        AuthorizationError: If user doesn't own the resource
    """
    user_id = current_user.get("id")
    
    if user_id != resource_owner_id:
        raise AuthorizationError(
            f"You don't have permission to access this {resource_type}",
            details={
                "user_id": user_id,
                "resource_owner_id": resource_owner_id,
                "resource_type": resource_type
            }
        )


def check_role_or_ownership(
    current_user: dict,
    allowed_roles: List[Union[UserRole, str]],
    resource_owner_id: str,
    action: str
) -> None:
    """
    Check if user has required role OR owns the resource.
    Useful for endpoints where admins can access any resource, but users can only access their own.
    
    Args:
        current_user: Current user dict
        allowed_roles: List of roles that have full access
        resource_owner_id: ID of the resource owner
        action: Description of the action
        
    Raises:
        AuthorizationError: If user doesn't have permission
        
    Example:
        >>> # Allow admin to view any manager's sellers, or manager to view their own
        >>> check_role_or_ownership(
        ...     current_user,
        ...     [UserRole.ADMIN],
        ...     manager_id,
        ...     "view sellers"
        ... )
    """
    user_role = current_user.get("role")
    user_id = current_user.get("id")
    
    # Convert allowed_roles to strings
    allowed_role_values = []
    for role in allowed_roles:
        if hasattr(role, 'value'):
            allowed_role_values.append(role.value)
        else:
            allowed_role_values.append(str(role))
    
    # Check if user has privileged role
    if user_role in allowed_role_values:
        return
    
    # Check if user owns the resource
    if user_id == resource_owner_id:
        return
    
    # Neither condition met - deny access
    raise AuthorizationError(
        f"Insufficient permissions to {action}. You must be in roles {allowed_role_values} or own this resource.",
        details={
            "required_roles": allowed_role_values,
            "user_role": user_role,
            "user_id": user_id,
            "resource_owner_id": resource_owner_id,
            "action": action
        }
    )
