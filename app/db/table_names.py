"""

If you are using Relational DB then you can use this file to store all the table names

Database Table Names Enum
Centralized table name constants to avoid hardcoding throughout the application
"""

from enum import Enum


class TableName(str, Enum):
    """
    Enum for all database table names.
    
    Usage:
        supabase.table(TableName.USERS).select("*").execute()
        
    Benefits:
        - Autocomplete support in IDEs
        - Type safety
        - Single source of truth
        - Easy refactoring if table names change
        - Prevents typos
    """
    
    # User-related tables
    USERS = "users"
    SUPERADMINS = "superadmins"
    ADMINS = "admins"
    MANAGERS = "managers"
    SELLERS = "sellers"
    

    
    # Storage buckets (not tables)
    BUCKET_PRODUCTS = "products"
    BUCKET_ORDERS = "orders"
    
    def __str__(self) -> str:
        """Return the string value when converted to string"""
        return self.value
