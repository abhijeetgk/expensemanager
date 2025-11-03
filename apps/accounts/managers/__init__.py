"""
Custom user manager with advanced OOP patterns.

Demonstrates:
- Manager pattern for custom querysets
- Factory pattern for user creation
- Type hints
- Docstrings
"""

from typing import Optional
from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom user manager that uses email as the unique identifier.
    
    This manager provides factory methods for creating users with
    proper validation and default values.
    """
    
    def create_user(
        self,
        email: str,
        username: str,
        password: Optional[str] = None,
        **extra_fields
    ):
        """
        Create and save a regular user with the given email and password.
        
        Args:
            email: User's email address
            username: User's username
            password: User's password
            **extra_fields: Additional fields
            
        Returns:
            User instance
            
        Raises:
            ValueError: If email or username is not provided
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
            
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            
        user.save(using=self._db)
        return user
    
    def create_superuser(
        self,
        email: str,
        username: str,
        password: Optional[str] = None,
        **extra_fields
    ):
        """
        Create and save a superuser with the given email and password.
        
        Args:
            email: User's email address
            username: User's username
            password: User's password
            **extra_fields: Additional fields
            
        Returns:
            User instance (superuser)
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, username, password, **extra_fields)
    
    def create_staff_user(
        self,
        email: str,
        username: str,
        password: Optional[str] = None,
        **extra_fields
    ):
        """
        Create and save a staff user (POWER_USER) with the given credentials.
        
        Args:
            email: User's email address
            username: User's username
            password: User's password
            **extra_fields: Additional fields
            
        Returns:
            User instance (power user)
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'POWER_USER')
        
        return self.create_user(email, username, password, **extra_fields)


class ActiveUserManager(models.Manager):
    """
    Manager that returns only active users.
    
    This demonstrates the use of custom managers for filtering.
    """
    
    def get_queryset(self):
        """Return only active users."""
        return super().get_queryset().filter(is_active=True, is_deleted=False)


class AdminUserManager(models.Manager):
    """Manager that returns only admin users."""
    
    def get_queryset(self):
        """Return only admin users."""
        return super().get_queryset().filter(role='ADMIN', is_active=True)


class PowerUserManager(models.Manager):
    """Manager that returns only power users."""
    
    def get_queryset(self):
        """Return only power users."""
        return super().get_queryset().filter(role='POWER_USER', is_active=True)

