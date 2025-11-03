# Expense Manager - Project Design Document

## Executive Summary
A comprehensive Django-based expense management system with role-based access control, real-time reporting, and advanced analytics.

## Technology Stack
- **Backend**: Django 5.0+ with Python 3.10+
- **Database**: PostgreSQL (production) / SQLite (development)
- **API**: Django REST Framework 3.14+
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Export**: openpyxl (Excel), ReportLab (PDF)
- **Charts**: Chart.js with Django integration
- **UI**: Bootstrap 5 with custom templates

## Database Design

### 1. User Management
```
User (extends AbstractBaseUser)
├── id: UUID (PK)
├── email: EmailField (unique)
├── username: CharField (unique)
├── first_name: CharField
├── last_name: CharField
├── role: CharField (ADMIN, POWER_USER, USER)
├── is_active: BooleanField
├── is_staff: BooleanField
├── date_joined: DateTimeField
├── last_login: DateTimeField
└── created_by: ForeignKey(User, null=True)

UserProfile
├── id: UUID (PK)
├── user: OneToOneField(User)
├── phone: CharField
├── avatar: ImageField
├── preferences: JSONField
└── timezone: CharField
```

### 2. Category Management
```
CategoryBase (Abstract)
├── id: UUID (PK)
├── name: CharField
├── description: TextField
├── icon: CharField
├── color: CharField
├── is_active: BooleanField
├── created_by: ForeignKey(User)
├── created_at: DateTimeField
└── updated_at: DateTimeField

IncomeCategory (extends CategoryBase)
└── (inherits all fields)

ExpenseCategory (extends CategoryBase)
└── (inherits all fields)
```

### 3. Transaction Management
```
TransactionBase (Abstract)
├── id: UUID (PK)
├── amount: DecimalField
├── description: TextField
├── date: DateField
├── created_by: ForeignKey(User)
├── created_at: DateTimeField
├── updated_at: DateTimeField
└── metadata: JSONField

Income (extends TransactionBase)
├── category: ForeignKey(IncomeCategory)
└── source: CharField

Expense (extends TransactionBase)
├── category: ForeignKey(ExpenseCategory)
├── payment_method: CharField
└── receipt: FileField
```

### 4. Budget & Planning
```
Budget
├── id: UUID (PK)
├── user: ForeignKey(User)
├── category: ForeignKey(ExpenseCategory)
├── amount: DecimalField
├── period: CharField (MONTHLY, QUARTERLY, YEARLY)
├── start_date: DateField
├── end_date: DateField
└── is_active: BooleanField
```

### 5. Reports & Analytics
```
Report
├── id: UUID (PK)
├── user: ForeignKey(User)
├── report_type: CharField
├── filters: JSONField
├── generated_at: DateTimeField
└── file: FileField
```

## Module Structure

```
expenseManager/
├── config/                      # Project configuration
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/               # User management
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── profile.py
│   │   ├── services/
│   │   │   └── user_service.py
│   │   ├── managers/
│   │   │   └── user_manager.py
│   │   ├── serializers/
│   │   ├── views/
│   │   ├── permissions.py
│   │   └── admin.py
│   │
│   ├── categories/             # Category management
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   ├── income.py
│   │   │   └── expense.py
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── serializers/
│   │   ├── views/
│   │   └── admin.py
│   │
│   ├── transactions/           # Income & Expense transactions
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   ├── income.py
│   │   │   └── expense.py
│   │   ├── services/
│   │   │   ├── transaction_service.py
│   │   │   └── validation_service.py
│   │   ├── factories/
│   │   │   └── transaction_factory.py
│   │   ├── serializers/
│   │   ├── views/
│   │   └── admin.py
│   │
│   ├── reports/                # Reporting & Analytics
│   │   ├── services/
│   │   │   ├── report_service.py
│   │   │   ├── export_service.py
│   │   │   └── analytics_service.py
│   │   ├── exporters/
│   │   │   ├── base.py
│   │   │   ├── excel.py
│   │   │   └── pdf.py
│   │   ├── views/
│   │   └── serializers/
│   │
│   ├── dashboard/              # Admin dashboard
│   │   ├── widgets/
│   │   │   ├── base.py
│   │   │   ├── chart_widget.py
│   │   │   └── stat_widget.py
│   │   ├── services/
│   │   │   └── dashboard_service.py
│   │   ├── views/
│   │   └── templates/
│   │
│   └── core/                   # Shared utilities
│       ├── models/
│       │   └── base.py
│       ├── mixins/
│       ├── decorators/
│       ├── exceptions.py
│       └── utils.py
│
├── static/
├── media/
├── templates/
└── tests/
```

## Advanced OOP Features Used

### 1. **Abstract Base Classes (ABC)**
- CategoryBase, TransactionBase for common functionality
- AbstractExporter for export strategies

### 2. **Mixins**
- TimeStampMixin for created_at/updated_at
- UserTrackingMixin for created_by/updated_by
- SoftDeleteMixin for soft deletion
- PermissionMixin for custom permissions

### 3. **Design Patterns**
- **Factory Pattern**: TransactionFactory for creating different transaction types
- **Strategy Pattern**: Different export strategies (Excel, PDF)
- **Repository Pattern**: Data access layer abstraction
- **Service Layer**: Business logic separation
- **Observer Pattern**: Signals for notifications
- **Singleton Pattern**: Configuration managers

### 4. **Modern Python Features**
- Type hints (typing module)
- Dataclasses for DTOs
- Context managers for resource handling
- Decorators for caching and permissions
- Async views where appropriate
- Property decorators for computed fields
- classmethod and staticmethod appropriately

### 5. **SOLID Principles**
- Single Responsibility: Each class has one purpose
- Open/Closed: Extensible through inheritance
- Liskov Substitution: Proper inheritance hierarchies
- Interface Segregation: Specific interfaces
- Dependency Injection: Services injected via constructors

## API Endpoints

### Authentication
```
POST   /api/auth/login/
POST   /api/auth/logout/
POST   /api/auth/refresh/
POST   /api/auth/register/
POST   /api/auth/password/reset/
```

### User Management (Admin)
```
GET    /api/admin/users/
POST   /api/admin/users/
GET    /api/admin/users/{id}/
PUT    /api/admin/users/{id}/
PATCH  /api/admin/users/{id}/
DELETE /api/admin/users/{id}/
PATCH  /api/admin/users/{id}/toggle-status/
```

### Categories (Admin)
```
GET    /api/admin/categories/income/
POST   /api/admin/categories/income/
PUT    /api/admin/categories/income/{id}/
DELETE /api/admin/categories/income/{id}/

GET    /api/admin/categories/expense/
POST   /api/admin/categories/expense/
PUT    /api/admin/categories/expense/{id}/
DELETE /api/admin/categories/expense/{id}/
```

### Categories (Power Users)
```
POST   /api/categories/income/quick-create/
POST   /api/categories/expense/quick-create/
```

### Transactions (User)
```
GET    /api/transactions/income/
POST   /api/transactions/income/
GET    /api/transactions/income/{id}/
PUT    /api/transactions/income/{id}/
DELETE /api/transactions/income/{id}/

GET    /api/transactions/expense/
POST   /api/transactions/expense/
GET    /api/transactions/expense/{id}/
PUT    /api/transactions/expense/{id}/
DELETE /api/transactions/expense/{id}/
```

### Reports
```
GET    /api/reports/summary/
GET    /api/reports/monthly/
GET    /api/reports/category-wise/
GET    /api/reports/period/
POST   /api/reports/export/excel/
POST   /api/reports/export/pdf/
```

### Dashboard (Admin)
```
GET    /api/dashboard/widgets/
GET    /api/dashboard/stats/
GET    /api/dashboard/charts/income-expense/
GET    /api/dashboard/charts/category-breakdown/
GET    /api/dashboard/charts/trend-analysis/
```

## User Roles & Permissions

### ADMIN
- Full system access
- User management (CRUD)
- Category management (CRUD)
- View all transactions
- Access all reports
- Dashboard access

### POWER_USER
- Own transactions (CRUD)
- Create categories on-the-fly
- View own reports
- Limited dashboard access

### USER
- Own transactions (CRUD)
- View existing categories
- View own reports

## Security Features
1. JWT authentication
2. CSRF protection
3. Rate limiting
4. Input validation
5. SQL injection prevention
6. XSS protection
7. Role-based access control
8. Audit logging

## Performance Optimizations
1. Database indexing
2. Query optimization (select_related, prefetch_related)
3. Caching (Redis)
4. Pagination
5. Lazy loading
6. Connection pooling

## Future Enhancements
1. Multi-currency support
2. Bank account integration
3. Recurring transactions
4. Mobile app API
5. Real-time notifications
6. Machine learning predictions
7. Budget recommendations
8. Receipt OCR scanning

