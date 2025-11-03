"""
Comprehensive test suite for the Expense Manager application.

Demonstrates:
- Unit tests
- Integration tests
- API tests
- Test fixtures
- Test utilities
"""

from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.categories.models import IncomeCategory, ExpenseCategory
from apps.transactions.models import Income, Expense
from apps.reports.services import ReportService

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test cases for User model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.admin = User.objects.create_user(
            email='admin@test.com',
            username='admin',
            password='admin123',
            role='ADMIN'
        )
        
        self.power_user = User.objects.create_user(
            email='poweruser@test.com',
            username='poweruser',
            password='power123',
            role='POWER_USER'
        )
        
        self.regular_user = User.objects.create_user(
            email='user@test.com',
            username='user',
            password='user123',
            role='USER'
        )
    
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(self.admin.role, 'ADMIN')
        self.assertEqual(self.power_user.role, 'POWER_USER')
        self.assertEqual(self.regular_user.role, 'USER')
    
    def test_user_permissions(self):
        """Test role-based permissions."""
        self.assertTrue(self.admin.is_admin)
        self.assertTrue(self.admin.can_manage_users())
        self.assertTrue(self.admin.can_manage_categories())
        
        self.assertTrue(self.power_user.is_power_user)
        self.assertFalse(self.power_user.can_manage_users())
        self.assertTrue(self.power_user.can_create_categories())
        
        self.assertTrue(self.regular_user.is_regular_user)
        self.assertFalse(self.regular_user.can_manage_users())
        self.assertFalse(self.regular_user.can_create_categories())
    
    def test_user_role_change(self):
        """Test changing user role."""
        self.regular_user.change_role('POWER_USER')
        self.assertEqual(self.regular_user.role, 'POWER_USER')
        self.assertTrue(self.regular_user.can_create_categories())


class CategoryModelTestCase(TestCase):
    """Test cases for Category models."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.admin = User.objects.create_user(
            email='admin@test.com',
            username='admin',
            password='admin123',
            role='ADMIN'
        )
        
        self.income_category = IncomeCategory.objects.create(
            name='Salary',
            description='Monthly salary',
            created_by=self.admin
        )
        
        self.expense_category = ExpenseCategory.objects.create(
            name='Food',
            description='Food and dining',
            budget_limit=Decimal('500.00'),
            created_by=self.admin
        )
    
    def test_category_creation(self):
        """Test category creation."""
        self.assertEqual(IncomeCategory.objects.count(), 1)
        self.assertEqual(ExpenseCategory.objects.count(), 1)
    
    def test_category_hierarchy(self):
        """Test category hierarchy."""
        child_category = ExpenseCategory.objects.create(
            name='Restaurants',
            parent=self.expense_category,
            created_by=self.admin
        )
        
        self.assertEqual(child_category.parent, self.expense_category)
        self.assertTrue(self.expense_category.is_root)
        self.assertFalse(child_category.is_root)
        self.assertEqual(child_category.depth, 1)
    
    def test_category_full_path(self):
        """Test category full path."""
        child_category = ExpenseCategory.objects.create(
            name='Restaurants',
            parent=self.expense_category,
            created_by=self.admin
        )
        
        self.assertEqual(
            child_category.full_path,
            'Food > Restaurants'
        )


class TransactionModelTestCase(TestCase):
    """Test cases for Transaction models."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            email='user@test.com',
            username='user',
            password='user123'
        )
        
        self.income_category = IncomeCategory.objects.create(
            name='Salary',
            created_by=self.user
        )
        
        self.expense_category = ExpenseCategory.objects.create(
            name='Food',
            created_by=self.user
        )
    
    def test_income_creation(self):
        """Test income transaction creation."""
        income = Income.objects.create(
            amount=Decimal('5000.00'),
            description='Monthly salary',
            transaction_date=date.today(),
            category=self.income_category,
            source='Company ABC',
            created_by=self.user
        )
        
        self.assertEqual(income.amount, Decimal('5000.00'))
        self.assertEqual(income.category, self.income_category)
        self.assertTrue(income.is_completed)
    
    def test_expense_creation(self):
        """Test expense transaction creation."""
        expense = Expense.objects.create(
            amount=Decimal('50.00'),
            description='Lunch',
            transaction_date=date.today(),
            category=self.expense_category,
            payment_method='CREDIT_CARD',
            vendor='Restaurant XYZ',
            created_by=self.user
        )
        
        self.assertEqual(expense.amount, Decimal('50.00'))
        self.assertEqual(expense.category, self.expense_category)
        self.assertEqual(expense.payment_method, 'CREDIT_CARD')
    
    def test_transaction_cancellation(self):
        """Test transaction cancellation."""
        income = Income.objects.create(
            amount=Decimal('5000.00'),
            description='Monthly salary',
            transaction_date=date.today(),
            category=self.income_category,
            source='Company ABC',
            created_by=self.user
        )
        
        income.cancel('Test cancellation')
        self.assertTrue(income.is_cancelled)
        self.assertIn('cancellation_reason', income.metadata)


class ReportServiceTestCase(TestCase):
    """Test cases for Report Service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            email='user@test.com',
            username='user',
            password='user123'
        )
        
        self.income_category = IncomeCategory.objects.create(
            name='Salary',
            created_by=self.user
        )
        
        self.expense_category = ExpenseCategory.objects.create(
            name='Food',
            created_by=self.user
        )
        
        # Create sample transactions
        Income.objects.create(
            amount=Decimal('5000.00'),
            description='Salary',
            transaction_date=date.today(),
            category=self.income_category,
            source='Company',
            created_by=self.user
        )
        
        Expense.objects.create(
            amount=Decimal('100.00'),
            description='Groceries',
            transaction_date=date.today(),
            category=self.expense_category,
            payment_method='CASH',
            created_by=self.user
        )
    
    def test_summary_report(self):
        """Test summary report generation."""
        report = ReportService.get_summary_report(self.user)
        
        self.assertEqual(report.total_income, Decimal('5000.00'))
        self.assertEqual(report.total_expense, Decimal('100.00'))
        self.assertEqual(report.net_balance, Decimal('4900.00'))
        self.assertEqual(report.transaction_count, 2)


class UserAPITestCase(APITestCase):
    """Test cases for User API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        self.admin = User.objects.create_user(
            email='admin@test.com',
            username='admin',
            password='admin123',
            role='ADMIN'
        )
        
        self.user = User.objects.create_user(
            email='user@test.com',
            username='user',
            password='user123'
        )
    
    def test_user_login(self):
        """Test user login."""
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@test.com',
            'password': 'admin123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_me_endpoint(self):
        """Test current user endpoint."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/accounts/users/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@test.com')
    
    def test_user_list_permission(self):
        """Test user list permissions."""
        # Regular user should only see themselves
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/accounts/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Admin should see all users
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/accounts/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)


class TransactionAPITestCase(APITestCase):
    """Test cases for Transaction API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            email='user@test.com',
            username='user',
            password='user123'
        )
        
        self.income_category = IncomeCategory.objects.create(
            name='Salary',
            created_by=self.user
        )
        
        self.expense_category = ExpenseCategory.objects.create(
            name='Food',
            created_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_create_income(self):
        """Test creating income transaction."""
        data = {
            'amount': '5000.00',
            'description': 'Monthly salary',
            'transaction_date': date.today().isoformat(),
            'category': str(self.income_category.id),
            'source': 'Company ABC'
        }
        
        response = self.client.post('/api/transactions/income/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Income.objects.count(), 1)
    
    def test_create_expense(self):
        """Test creating expense transaction."""
        data = {
            'amount': '50.00',
            'description': 'Lunch',
            'transaction_date': date.today().isoformat(),
            'category': str(self.expense_category.id),
            'payment_method': 'CREDIT_CARD',
            'vendor': 'Restaurant XYZ'
        }
        
        response = self.client.post('/api/transactions/expense/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)
    
    def test_list_transactions(self):
        """Test listing transactions."""
        # Create some transactions
        Income.objects.create(
            amount=Decimal('5000.00'),
            description='Salary',
            transaction_date=date.today(),
            category=self.income_category,
            source='Company',
            created_by=self.user
        )
        
        response = self.client.get('/api/transactions/income/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


# Run tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["__main__"])

