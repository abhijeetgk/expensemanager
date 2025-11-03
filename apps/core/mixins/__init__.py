"""
Base models and mixins for the Expense Manager application.

This module demonstrates advanced OOP patterns:
- Abstract Base Classes
- Mixins for reusable functionality
- UUID primary keys
- Type hints
- Property decorators
"""

import uuid
from typing import Any
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


class TimeStampMixin(models.Model):
    """
    Abstract mixin that provides timestamp fields.
    
    This mixin adds created_at and updated_at fields to any model
    that inherits from it. Uses the Template Method pattern.
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text="Timestamp when the record was last updated"
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
        
    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Override save to add custom timestamp logic if needed.
        """
        super().save(*args, **kwargs)


class UserTrackingMixin(models.Model):
    """
    Abstract mixin that tracks which user created/updated a record.
    
    Demonstrates:
    - Lazy evaluation of ForeignKey
    - Null safety
    """
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text="User who last updated this record"
    )
    
    class Meta:
        abstract = True
        
    @property
    def creator_name(self) -> str:
        """Get the name of the creator."""
        return self.created_by.get_full_name() if self.created_by else "System"


class SoftDeleteMixin(models.Model):
    """
    Abstract mixin for soft deletion functionality.
    
    Instead of permanently deleting records, we mark them as deleted.
    This is useful for maintaining data integrity and audit trails.
    """
    
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Soft delete flag"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the record was soft deleted"
    )
    deleted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        help_text="User who deleted this record"
    )
    
    class Meta:
        abstract = True
        
    def soft_delete(self, user=None) -> None:
        """
        Soft delete the record.
        
        Args:
            user: The user performing the deletion
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
        
    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
        
    @property
    def is_active(self) -> bool:
        """Check if the record is active (not deleted)."""
        return not self.is_deleted


class UUIDPrimaryKeyMixin(models.Model):
    """
    Abstract mixin that provides a UUID primary key.
    
    UUIDs are better for distributed systems and don't expose
    the number of records in the database.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record"
    )
    
    class Meta:
        abstract = True


class BaseModel(UUIDPrimaryKeyMixin, TimeStampMixin, UserTrackingMixin):
    """
    Base model that combines all common mixins.
    
    This demonstrates the Mixin pattern and provides a solid
    foundation for all domain models.
    """
    
    class Meta:
        abstract = True
        
    def __str__(self) -> str:
        """
        String representation of the model.
        Subclasses should override this.
        """
        return f"{self.__class__.__name__}({self.id})"
        
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<{self.__class__.__name__} id={self.id}>"


class ActivatableMixin(models.Model):
    """
    Mixin for models that can be activated/deactivated.
    
    This is useful for categories, users, and other entities
    that might need to be temporarily disabled.
    """
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this record is active"
    )
    
    class Meta:
        abstract = True
        
    def activate(self) -> None:
        """Activate the record."""
        self.is_active = True
        self.save(update_fields=['is_active'])
        
    def deactivate(self) -> None:
        """Deactivate the record."""
        self.is_active = False
        self.save(update_fields=['is_active'])
        
    def toggle_active(self) -> bool:
        """Toggle the active status and return the new state."""
        self.is_active = not self.is_active
        self.save(update_fields=['is_active'])
        return self.is_active

