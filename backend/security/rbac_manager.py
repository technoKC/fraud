from functools import wraps
from fastapi import HTTPException, status
from typing import List, Callable

class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self, security_manager):
        self.security_manager = security_manager
    
    def require_permission(self, permission: str):
        """Decorator to require specific permission for endpoint"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get current user from kwargs
                current_user = kwargs.get('current_user')
                if not current_user:
                    # Try to get from the last argument if it's a dict
                    for arg in args:
                        if isinstance(arg, dict) and 'role' in arg:
                            current_user = arg
                            break
                    
                    if not current_user:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication required"
                        )
                
                # Check permission
                user_role = current_user.get('role')
                if not user_role:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid user role"
                    )
                
                if not self.security_manager.check_permission(user_role, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied. Required: {permission}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def require_any_permission(self, permissions: List[str]):
        """Decorator to require any of the specified permissions"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                current_user = kwargs.get('current_user')
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                user_role = current_user.get('role')
                has_permission = any(
                    self.security_manager.check_permission(user_role, perm) 
                    for perm in permissions
                )
                
                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied. Required one of: {', '.join(permissions)}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def require_all_permissions(self, permissions: List[str]):
        """Decorator to require all specified permissions"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                current_user = kwargs.get('current_user')
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                user_role = current_user.get('role')
                has_all_permissions = all(
                    self.security_manager.check_permission(user_role, perm) 
                    for perm in permissions
                )
                
                if not has_all_permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied. Required all: {', '.join(permissions)}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator