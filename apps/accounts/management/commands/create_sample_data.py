"""
Management command to create sample data for testing.

This demonstrates:
- Django management commands
- Factory pattern for data creation
- Bulk operations
"""

from decimal import Decimal
from datetime import datetime, timedelta
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.categories.models import IncomeCategory, ExpenseCategory
from apps.transactions.models import Income, Expense

User = get_user_model()


class Command(BaseCommand):
    """Create sample data for the expense manager."""
    
    help = 'Create sample users, categories, and transactions for testing'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of regular users to create'
        )
        parser.add_argument(
            '--transactions',
            type=int,
            default=50,
            help='Number of transactions per user'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        num_users = options['users']
        num_transactions = options['transactions']
        
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create admin user
        admin = self._create_admin()
        self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.email}'))
        
        # Create power user
        power_user = self._create_power_user()
        self.stdout.write(self.style.SUCCESS(f'Created power user: {power_user.email}'))
        
        # Create regular users
        users = self._create_regular_users(num_users)
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} regular users'))
        
        # Create categories
        income_categories = self._create_income_categories(admin)
        expense_categories = self._create_expense_categories(admin)
        self.stdout.write(self.style.SUCCESS(
            f'Created {len(income_categories)} income categories and '
            f'{len(expense_categories)} expense categories'
        ))
        
        # Create transactions
        all_users = [admin, power_user] + users
        total_transactions = 0
        
        for user in all_users:
            count = self._create_transactions(
                user, income_categories, expense_categories, num_transactions
            )
            total_transactions += count
        
        self.stdout.write(self.style.SUCCESS(
            f'Created {total_transactions} transactions'
        ))
        
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write(f'  Admin: admin@example.com / admin123')
        self.stdout.write(f'  Power User: poweruser@example.com / power123')
        self.stdout.write(f'  Regular Users: user1@example.com / user123, etc.')
    
    def _create_admin(self):
        """Create admin user."""
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        return admin
    
    def _create_power_user(self):
        """Create power user."""
        power_user, created = User.objects.get_or_create(
            email='poweruser@example.com',
            defaults={
                'username': 'poweruser',
                'first_name': 'Power',
                'last_name': 'User',
                'role': 'POWER_USER',
                'is_staff': True,
            }
        )
        if created:
            power_user.set_password('power123')
            power_user.save()
        return power_user
    
    def _create_regular_users(self, count):
        """Create regular users."""
        users = []
        for i in range(1, count + 1):
            user, created = User.objects.get_or_create(
                email=f'user{i}@example.com',
                defaults={
                    'username': f'user{i}',
                    'first_name': f'User',
                    'last_name': f'{i}',
                    'role': 'USER',
                }
            )
            if created:
                user.set_password('user123')
                user.save()
            users.append(user)
        return users
    
    def _create_income_categories(self, admin):
        """Create income categories."""
        categories = [
            {'name': 'Salary', 'icon': 'fas fa-briefcase', 'color': '#10B981', 'is_recurring': True, 'tax_applicable': True},
            {'name': 'Freelance', 'icon': 'fas fa-laptop', 'color': '#3B82F6', 'is_recurring': False, 'tax_applicable': True},
            {'name': 'Investment', 'icon': 'fas fa-chart-line', 'color': '#8B5CF6', 'is_recurring': False, 'tax_applicable': True},
            {'name': 'Bonus', 'icon': 'fas fa-gift', 'color': '#F59E0B', 'is_recurring': False, 'tax_applicable': True},
            {'name': 'Gift', 'icon': 'fas fa-heart', 'color': '#EF4444', 'is_recurring': False, 'tax_applicable': False},
        ]
        
        created_categories = []
        for cat_data in categories:
            category, _ = IncomeCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'created_by': admin,
                    **cat_data
                }
            )
            created_categories.append(category)
        
        return created_categories
    
    def _create_expense_categories(self, admin):
        """Create expense categories."""
        categories = [
            {'name': 'Food & Dining', 'icon': 'fas fa-utensils', 'color': '#EF4444', 'is_essential': True, 'budget_limit': Decimal('500.00')},
            {'name': 'Transportation', 'icon': 'fas fa-car', 'color': '#F59E0B', 'is_essential': True, 'budget_limit': Decimal('300.00')},
            {'name': 'Shopping', 'icon': 'fas fa-shopping-bag', 'color': '#8B5CF6', 'is_essential': False, 'budget_limit': Decimal('400.00')},
            {'name': 'Healthcare', 'icon': 'fas fa-hospital', 'color': '#10B981', 'is_essential': True, 'budget_limit': Decimal('200.00')},
            {'name': 'Entertainment', 'icon': 'fas fa-film', 'color': '#3B82F6', 'is_essential': False, 'budget_limit': Decimal('200.00')},
            {'name': 'Utilities', 'icon': 'fas fa-bolt', 'color': '#F97316', 'is_essential': True, 'budget_limit': Decimal('150.00')},
            {'name': 'Education', 'icon': 'fas fa-graduation-cap', 'color': '#06B6D4', 'is_essential': True, 'budget_limit': Decimal('300.00')},
            {'name': 'Travel', 'icon': 'fas fa-plane', 'color': '#EC4899', 'is_essential': False, 'budget_limit': Decimal('500.00')},
        ]
        
        created_categories = []
        for cat_data in categories:
            category, _ = ExpenseCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'created_by': admin,
                    **cat_data
                }
            )
            created_categories.append(category)
        
        return created_categories
    
    def _create_transactions(self, user, income_categories, expense_categories, count):
        """Create random transactions for a user."""
        transaction_count = 0
        
        # Create income transactions (20% of total)
        income_count = count // 5
        for _ in range(income_count):
            category = random.choice(income_categories)
            days_ago = random.randint(0, 365)
            transaction_date = timezone.now().date() - timedelta(days=days_ago)
            
            Income.objects.create(
                amount=Decimal(random.uniform(1000, 10000)),
                description=f'Income from {category.name}',
                transaction_date=transaction_date,
                category=category,
                source=f'{category.name} Source',
                is_recurring=category.is_recurring,
                tax_amount=Decimal(random.uniform(0, 500)),
                created_by=user,
                status='COMPLETED'
            )
            transaction_count += 1
        
        # Create expense transactions (80% of total)
        expense_count = count - income_count
        for _ in range(expense_count):
            category = random.choice(expense_categories)
            days_ago = random.randint(0, 365)
            transaction_date = timezone.now().date() - timedelta(days=days_ago)
            
            payment_methods = ['CASH', 'CREDIT_CARD', 'DEBIT_CARD', 'BANK_TRANSFER']
            
            Expense.objects.create(
                amount=Decimal(random.uniform(10, 1000)),
                description=f'Expense for {category.name}',
                transaction_date=transaction_date,
                category=category,
                payment_method=random.choice(payment_methods),
                vendor=f'{category.name} Vendor',
                is_reimbursable=random.choice([True, False]),
                reimbursed=False,
                created_by=user,
                status='COMPLETED'
            )
            transaction_count += 1
        
        return transaction_count

