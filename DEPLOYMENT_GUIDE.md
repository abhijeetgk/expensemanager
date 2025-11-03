# Expense Manager - Deployment & Setup Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (venv)
- PostgreSQL (for production) or SQLite (for development)
- Redis (optional, for caching)

## Installation Steps

### 1. Clone the Repository

```bash
cd /path/to/your/project
```

### 2. Create and Activate Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root (optional, defaults are set in settings.py):

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# For PostgreSQL (production)
# DATABASE_URL=postgresql://user:password@localhost:5432/expense_manager

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Redis Cache (optional)
# REDIS_URL=redis://localhost:6379/1
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create Sample Data (Optional)

```bash
python manage.py create_sample_data --users=5 --transactions=50
```

This creates:
- 1 Admin user (admin@example.com / admin123)
- 1 Power user (poweruser@example.com / power123)
- 5 Regular users (user1@example.com / user123, etc.)
- Income and expense categories
- Sample transactions for all users

### 7. Create Superuser (Manual)

If you prefer to create your own admin:

```bash
python manage.py createsuperuser
```

### 8. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 9. Run Development Server

```bash
python manage.py runserver
```

The application will be available at: `http://localhost:8000`

## Access Points

### Admin Panel
- URL: `http://localhost:8000/admin/`
- Login with superuser credentials or:
  - Email: admin@example.com
  - Password: admin123

### API Endpoints
- Base URL: `http://localhost:8000/api/`
- Documentation: See `API_DOCUMENTATION.md`

### API Authentication
```bash
# Get access token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Use the access token
curl -X GET http://localhost:8000/api/accounts/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test tests.test_suite

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Project Structure

```
expenseManager/
├── config/                     # Project configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL configuration
│   └── wsgi.py                # WSGI configuration
│
├── apps/                       # Django applications
│   ├── accounts/              # User management
│   │   ├── models.py          # User model with roles
│   │   ├── views.py           # User API views
│   │   ├── serializers.py     # User serializers
│   │   ├── permissions.py     # Custom permissions
│   │   └── admin.py           # Admin interface
│   │
│   ├── categories/            # Category management
│   │   ├── models.py          # Income/Expense categories
│   │   ├── views.py           # Category API views
│   │   └── admin.py           # Admin interface
│   │
│   ├── transactions/          # Income & Expense transactions
│   │   ├── models.py          # Transaction models
│   │   ├── views.py           # Transaction API views
│   │   └── admin.py           # Admin interface
│   │
│   ├── reports/               # Reporting & Analytics
│   │   ├── services/          # Business logic layer
│   │   │   └── __init__.py    # Report services
│   │   ├── exporters/         # Export strategies
│   │   │   └── __init__.py    # Excel/PDF exporters
│   │   └── views.py           # Report API views
│   │
│   ├── dashboard/             # Admin dashboard
│   │   └── views.py           # Dashboard widgets & charts
│   │
│   └── core/                  # Shared utilities
│       └── mixins/            # Reusable model mixins
│
├── static/                    # Static files
├── media/                     # User uploads
├── templates/                 # HTML templates
├── tests/                     # Test suite
│   └── test_suite.py         # Comprehensive tests
│
├── requirements.txt           # Python dependencies
├── manage.py                  # Django management script
├── README.md                  # Project overview
├── PROJECT_DESIGN.md          # Detailed design document
└── API_DOCUMENTATION.md       # API documentation
```

## Advanced OOP Features Used

### 1. Abstract Base Classes (ABC)
- `CategoryBase`: Base for income/expense categories
- `TransactionBase`: Base for income/expense transactions
- `ExporterBase`: Abstract export strategy

### 2. Mixins
- `TimeStampMixin`: Automatic timestamp tracking
- `UserTrackingMixin`: User creation/modification tracking
- `SoftDeleteMixin`: Soft deletion functionality
- `ActivatableMixin`: Activation/deactivation

### 3. Design Patterns
- **Strategy Pattern**: Export strategies (Excel, PDF)
- **Factory Pattern**: User creation in managers
- **Service Layer**: Business logic separation
- **Repository Pattern**: Data access abstraction
- **Observer Pattern**: Django signals
- **Template Method**: Base classes with hooks

### 4. Modern Python Features
- Type hints throughout
- Dataclasses for DTOs
- Property decorators
- Context managers
- Enum-like classes
- classmethod and staticmethod

### 5. SOLID Principles
- **Single Responsibility**: Each class has one purpose
- **Open/Closed**: Extensible through inheritance
- **Liskov Substitution**: Proper inheritance hierarchies
- **Interface Segregation**: Specific interfaces
- **Dependency Injection**: Services injected

## Key Features

### User Management
- Custom user model with email authentication
- Role-based access control (Admin, Power User, User)
- Permission system based on roles
- User activation/deactivation

### Category Management
- Hierarchical category structure
- Separate income and expense categories
- Budget limits for expense categories
- Quick category creation for power users

### Transaction Management
- Income and expense tracking
- Multiple payment methods
- Recurring transactions
- Reimbursement tracking
- Tagging system
- Soft delete functionality

### Reporting & Analytics
- Summary reports
- Monthly reports
- Category-wise breakdown
- Trend analysis
- Budget analysis
- Spending patterns
- Top expenses

### Export Functionality
- Export to Excel (.xlsx)
- Export to PDF
- Customizable date ranges
- Formatted output with styling

### Admin Dashboard
- System statistics
- Income vs Expense charts
- Category breakdown charts
- Top users widget
- Recent transactions widget

## API Features

### Authentication
- JWT-based authentication
- Token refresh mechanism
- Secure password hashing

### Permissions
- Role-based permissions
- Object-level permissions
- Custom permission classes

### Filtering & Search
- Query parameter filtering
- Full-text search
- Date range filtering
- Ordering/sorting

### Pagination
- Page-based pagination
- Configurable page size
- Next/previous links

## Development Tips

### Adding New Features

1. **Create Models**: Add models in `apps/<app>/models.py`
2. **Create Serializers**: Add serializers in `apps/<app>/serializers.py`
3. **Create Views**: Add views in `apps/<app>/views.py`
4. **Configure URLs**: Add URLs in `apps/<app>/urls.py`
5. **Add Tests**: Add tests in `tests/`
6. **Update Admin**: Add admin configuration in `apps/<app>/admin.py`

### Running Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Django Shell

```bash
# Open Django shell
python manage.py shell

# Example queries
from apps.accounts.models import User
from apps.transactions.models import Income, Expense

# Get all users
users = User.objects.all()

# Get transactions for a user
user = User.objects.first()
incomes = Income.objects.for_user(user)
expenses = Expense.objects.for_user(user)
```

## Production Deployment

### PostgreSQL Setup

```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Create database
createdb expense_manager

# Update settings.py or .env
DATABASE_URL=postgresql://user:password@localhost:5432/expense_manager
```

### Gunicorn Setup

```bash
# Install Gunicorn (already in requirements.txt)
pip install gunicorn

# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@localhost:5432/expense_manager
```

## Troubleshooting

### Common Issues

1. **Migration errors**: Delete db.sqlite3 and run migrations again
2. **Port already in use**: Use a different port: `python manage.py runserver 8001`
3. **Permission errors**: Check file permissions and ownership
4. **Static files not loading**: Run `python manage.py collectstatic`

### Getting Help

- Check the logs in `logs/django.log`
- Review Django documentation: https://docs.djangoproject.com/
- Check DRF documentation: https://www.django-rest-framework.org/

## License

MIT License

## Support

For issues and questions, please refer to the documentation or create an issue in the repository.

