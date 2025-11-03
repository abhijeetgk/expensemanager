"""
Custom User model with role-based permissions.

Demonstrates advanced OOP concepts:
- Inheritance from AbstractBaseUser and PermissionsMixin
- Custom managers
- Property decorators
- Enum-like choices
- Type hints
- Rich string representations
"""

import uuid
from typing import Optional
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.mixins import TimeStampMixin, SoftDeleteMixin
from apps.accounts.managers import (
    UserManager,
    ActiveUserManager,
    AdminUserManager,
    PowerUserManager
)


class UserRole:
    """
    Enum-like class for user roles.
    
    This provides a centralized place for role definitions
    and makes the code more maintainable.
    """
    ADMIN = 'ADMIN'
    POWER_USER = 'POWER_USER'
    USER = 'USER'
    
    CHOICES = [
        (ADMIN, _('Administrator')),
        (POWER_USER, _('Power User')),
        (USER, _('Regular User')),
    ]
    
    @classmethod
    def get_role_permissions(cls, role: str) -> dict:
        """
        Get permissions for a specific role.
        
        Args:
            role: The role to get permissions for
            
        Returns:
            Dictionary of permissions
        """
        permissions = {
            cls.ADMIN: {
                'can_manage_users': True,
                'can_manage_categories': True,
                'can_view_all_transactions': True,
                'can_manage_settings': True,
                'can_create_categories': True,
            },
            cls.POWER_USER: {
                'can_manage_users': False,
                'can_manage_categories': False,
                'can_view_all_transactions': False,
                'can_manage_settings': False,
                'can_create_categories': True,
            },
            cls.USER: {
                'can_manage_users': False,
                'can_manage_categories': False,
                'can_view_all_transactions': False,
                'can_manage_settings': False,
                'can_create_categories': False,
            },
        }
        return permissions.get(role, permissions[cls.USER])


class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin, SoftDeleteMixin):
    """
    Custom user model using email as the unique identifier.
    
    This model demonstrates:
    - Multiple inheritance
    - UUID primary key
    - Role-based permissions
    - Custom managers
    - Property decorators
    - Comprehensive validation
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for this user")
    )
    
    email = models.EmailField(
        _('email address'),
        unique=True,
        db_index=True,
        help_text=_("User's email address (used for login)")
    )
    
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        db_index=True,
        help_text=_("User's unique username")
    )
    
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=True,
        help_text=_("User's first name")
    )
    
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=True,
        help_text=_("User's last name")
    )
    
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=UserRole.CHOICES,
        default=UserRole.USER,
        db_index=True,
        help_text=_("User's role in the system")
    )
    
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_("Designates whether the user can log into the admin site")
    )
    
    is_active = models.BooleanField(
        _('active'),
        default=True,
        db_index=True,
        help_text=_("Designates whether this user should be treated as active")
    )
    
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
        help_text=_("Date and time when the user joined")
    )
    
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        help_text=_("User's phone number")
    )
    
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text=_("User's profile picture")
    )
    
    bio = models.TextField(
        _('biography'),
        blank=True,
        help_text=_("User's biography or description")
    )
    
    preferences = models.JSONField(
        _('preferences'),
        default=dict,
        blank=True,
        help_text=_("User's preferences and settings")
    )
    
    timezone = models.CharField(
        _('timezone'),
        max_length=50,
        default='UTC',
        help_text=_("User's preferred timezone")
    )
    
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_created',
        help_text=_("User who created this account")
    )
    
    last_login_ip = models.GenericIPAddressField(
        _('last login IP'),
        null=True,
        blank=True,
        help_text=_("IP address of the last login")
    )
    
    # Managers
    objects = UserManager()
    active = ActiveUserManager()
    admins = AdminUserManager()
    power_users = PowerUserManager()
    
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self) -> str:
        """String representation of the user."""
        return self.email
        
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<User {self.email} ({self.role})>"
    
    def get_full_name(self) -> str:
        """
        Return the first_name plus the last_name, with a space in between.
        
        Returns:
            Full name of the user
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
    
    def get_short_name(self) -> str:
        """
        Return the short name for the user.
        
        Returns:
            First name or username
        """
        return self.first_name or self.username
    
    @property
    def is_admin(self) -> bool:
        """Check if the user is an administrator."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_power_user(self) -> bool:
        """Check if the user is a power user."""
        return self.role == UserRole.POWER_USER
    
    @property
    def is_regular_user(self) -> bool:
        """Check if the user is a regular user."""
        return self.role == UserRole.USER
    
    @property
    def permissions(self) -> dict:
        """
        Get role-based permissions for the user.
        
        Returns:
            Dictionary of permissions
        """
        return UserRole.get_role_permissions(self.role)
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if the user has a specific permission.
        
        Args:
            permission: The permission to check
            
        Returns:
            True if the user has the permission, False otherwise
        """
        return self.permissions.get(permission, False)
    
    def can_manage_users(self) -> bool:
        """Check if the user can manage other users."""
        return self.has_permission('can_manage_users')
    
    def can_manage_categories(self) -> bool:
        """Check if the user can manage categories."""
        return self.has_permission('can_manage_categories')
    
    def can_create_categories(self) -> bool:
        """Check if the user can create categories on-the-fly."""
        return self.has_permission('can_create_categories')
    
    def can_view_all_transactions(self) -> bool:
        """Check if the user can view all transactions."""
        return self.has_permission('can_view_all_transactions')
    
    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
        self.save(update_fields=['is_active'])
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    def change_role(self, new_role: str) -> None:
        """
        Change the user's role.
        
        Args:
            new_role: The new role to assign
            
        Raises:
            ValueError: If the role is invalid
        """
        valid_roles = [role[0] for role in UserRole.CHOICES]
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {valid_roles}")
        
        self.role = new_role
        
        # Update staff status based on role
        if new_role == UserRole.ADMIN:
            self.is_staff = True
        
        self.save(update_fields=['role', 'is_staff'])
    
    def update_last_login_info(self, ip_address: Optional[str] = None) -> None:
        """
        Update last login information.
        
        Args:
            ip_address: The IP address of the login
        """
        self.last_login = timezone.now()
        if ip_address:
            self.last_login_ip = ip_address
        self.save(update_fields=['last_login', 'last_login_ip'])

