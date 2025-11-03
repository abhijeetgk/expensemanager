"""
Category models for income and expense tracking.

Demonstrates:
- Abstract base classes
- Template Method pattern
- Inheritance hierarchies
- DRY principles
- Custom managers
"""

from typing import ClassVar
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from apps.core.mixins import BaseModel, ActivatableMixin


class CategoryManager(models.Manager):
    """Custom manager for categories."""
    
    def active(self):
        """Return only active categories."""
        return self.filter(is_active=True, is_deleted=False)
    
    def for_user(self, user):
        """
        Get categories available to a specific user.
        
        Args:
            user: The user to filter categories for
            
        Returns:
            QuerySet of available categories
        """
        if user.is_admin:
            return self.active()
        return self.active()


class CategoryBase(BaseModel, ActivatableMixin):
    """
    Abstract base class for all categories.
    
    This class demonstrates the Template Method pattern and provides
    common functionality for both income and expense categories.
    
    Attributes:
        name: Category name
        description: Category description
        icon: Icon identifier for the category
        color: Color code for UI display
    """
    
    # Class variable to track category type
    category_type: ClassVar[str] = "BASE"
    
    name = models.CharField(
        _('name'),
        max_length=100,
        db_index=True,
        help_text=_("Name of the category")
    )
    
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Detailed description of the category")
    )
    
    icon = models.CharField(
        _('icon'),
        max_length=50,
        blank=True,
        help_text=_("Icon identifier (e.g., Font Awesome class)")
    )
    
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#3B82F6',
        validators=[
            RegexValidator(
                regex=r'^#[0-9A-Fa-f]{6}$',
                message='Color must be a valid hex color code (e.g., #FF5733)'
            )
        ],
        help_text=_("Hex color code for the category")
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text=_("Parent category for creating hierarchies")
    )
    
    sort_order = models.IntegerField(
        _('sort order'),
        default=0,
        help_text=_("Order in which the category should appear")
    )
    
    objects = CategoryManager()
    
    class Meta:
        abstract = True
        ordering = ['sort_order', 'name']
        
    def __str__(self) -> str:
        """String representation of the category."""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"<{self.__class__.__name__} {self.name}>"
    
    @property
    def full_path(self) -> str:
        """
        Get the full hierarchical path of the category.
        
        Returns:
            Full path string (e.g., "Parent > Child > Grandchild")
        """
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    @property
    def depth(self) -> int:
        """
        Calculate the depth of the category in the hierarchy.
        
        Returns:
            Depth level (0 for root categories)
        """
        if self.parent:
            return 1 + self.parent.depth
        return 0
    
    @property
    def is_root(self) -> bool:
        """Check if this is a root category."""
        return self.parent is None
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf category (no children)."""
        return not self.subcategories.exists()
    
    def get_ancestors(self):
        """
        Get all ancestor categories.
        
        Returns:
            List of ancestor categories
        """
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return list(reversed(ancestors))
    
    def get_descendants(self):
        """
        Get all descendant categories recursively.
        
        Returns:
            QuerySet of descendant categories
        """
        descendants = []
        for child in self.subcategories.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_siblings(self):
        """
        Get sibling categories (same parent).
        
        Returns:
            QuerySet of sibling categories
        """
        if self.parent:
            return self.parent.subcategories.exclude(id=self.id)
        return self.__class__.objects.filter(parent__isnull=True).exclude(id=self.id)
    
    @classmethod
    def get_root_categories(cls):
        """
        Get all root categories.
        
        Returns:
            QuerySet of root categories
        """
        return cls.objects.filter(parent__isnull=True, is_active=True)
    
    def validate_hierarchy(self) -> bool:
        """
        Validate that the category hierarchy is valid.
        
        Returns:
            True if valid, raises ValidationError otherwise
        """
        from django.core.exceptions import ValidationError
        
        # Check for circular reference
        current = self.parent
        visited = {self.id}
        
        while current:
            if current.id in visited:
                raise ValidationError(_("Circular reference detected in category hierarchy"))
            visited.add(current.id)
            current = current.parent
        
        return True
    
    def save(self, *args, **kwargs):
        """
        Override save to validate hierarchy.
        """
        if self.parent:
            self.validate_hierarchy()
        super().save(*args, **kwargs)


class IncomeCategory(CategoryBase):
    """
    Income category model.
    
    Represents categories for income transactions such as:
    - Salary
    - Freelance
    - Investments
    - Gifts
    """
    
    category_type = "INCOME"
    
    # Income-specific fields
    is_recurring = models.BooleanField(
        _('is recurring'),
        default=False,
        help_text=_("Whether this income type is typically recurring")
    )
    
    tax_applicable = models.BooleanField(
        _('tax applicable'),
        default=False,
        help_text=_("Whether income from this category is taxable")
    )
    
    class Meta:
        verbose_name = _('Income Category')
        verbose_name_plural = _('Income Categories')
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['name', 'is_active']),
            models.Index(fields=['created_by', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'parent'],
                name='unique_income_category_name_parent'
            )
        ]


class ExpenseCategory(CategoryBase):
    """
    Expense category model.
    
    Represents categories for expense transactions such as:
    - Food & Dining
    - Transportation
    - Healthcare
    - Entertainment
    - Utilities
    """
    
    category_type = "EXPENSE"
    
    # Expense-specific fields
    budget_limit = models.DecimalField(
        _('budget limit'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Optional budget limit for this category")
    )
    
    is_essential = models.BooleanField(
        _('is essential'),
        default=False,
        help_text=_("Whether this expense category is essential (vs discretionary)")
    )
    
    allows_split = models.BooleanField(
        _('allows split'),
        default=True,
        help_text=_("Whether expenses in this category can be split across multiple categories")
    )
    
    class Meta:
        verbose_name = _('Expense Category')
        verbose_name_plural = _('Expense Categories')
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['name', 'is_active']),
            models.Index(fields=['created_by', 'is_active']),
            models.Index(fields=['is_essential', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'parent'],
                name='unique_expense_category_name_parent'
            )
        ]
    
    @property
    def is_over_budget(self) -> bool:
        """
        Check if expenses in this category exceed the budget.
        
        Returns:
            True if over budget, False otherwise
        """
        if not self.budget_limit:
            return False
        
        # This will be implemented when we have transactions
        # For now, return False
        return False
    
    def get_budget_utilization(self) -> float:
        """
        Calculate budget utilization percentage.
        
        Returns:
            Percentage of budget used (0-100+)
        """
        if not self.budget_limit:
            return 0.0
        
        # This will be implemented when we have transactions
        # For now, return 0.0
        return 0.0

