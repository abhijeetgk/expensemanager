# Expense Manager

A comprehensive Django-based expense management system with role-based access control, real-time reporting, and advanced analytics.

## Features

- **User Management**: Multi-role user system (Admin, Power User, User)
- **Category Management**: Dynamic income and expense categories
- **Transaction Tracking**: Detailed income and expense entries
- **Advanced Reporting**: Month-wise, category-wise, and period-based reports
- **Data Export**: Export reports to Excel and PDF
- **Admin Dashboard**: Rich UI with charts and widgets
- **RESTful API**: Complete API for all operations
- **Role-Based Permissions**: Granular access control

## Technology Stack

- **Backend**: Django 5.0 with Python 3.10+
- **API**: Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: PostgreSQL / SQLite
- **Export**: openpyxl, ReportLab
- **Caching**: Redis

## Quick Start

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

## Project Structure

```
expenseManager/
├── config/                 # Project configuration
├── apps/
│   ├── accounts/          # User management
│   ├── categories/        # Category management
│   ├── transactions/      # Income & Expense transactions
│   ├── reports/           # Reporting & Analytics
│   ├── dashboard/         # Admin dashboard
│   └── core/              # Shared utilities
├── static/                # Static files
├── media/                 # User uploads
└── templates/             # HTML templates
```

## API Documentation

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh token
- `POST /api/auth/logout/` - User logout

### Users (Admin)
- `GET /api/admin/users/` - List all users
- `POST /api/admin/users/` - Create user
- `GET /api/admin/users/{id}/` - Get user details
- `PUT /api/admin/users/{id}/` - Update user
- `DELETE /api/admin/users/{id}/` - Delete user

### Categories
- `GET /api/admin/categories/income/` - List income categories
- `POST /api/admin/categories/income/` - Create income category
- `GET /api/admin/categories/expense/` - List expense categories
- `POST /api/admin/categories/expense/` - Create expense category

### Transactions
- `GET /api/transactions/income/` - List income transactions
- `POST /api/transactions/income/` - Create income
- `GET /api/transactions/expense/` - List expense transactions
- `POST /api/transactions/expense/` - Create expense

### Reports
- `GET /api/reports/summary/` - Get summary report
- `GET /api/reports/monthly/` - Get monthly report
- `POST /api/reports/export/excel/` - Export to Excel
- `POST /api/reports/export/pdf/` - Export to PDF

## User Roles

### Admin
- Full system access
- User management
- Category management
- View all transactions
- Access all reports

### Power User
- Manage own transactions
- Create categories on-the-fly
- View own reports

### User
- Manage own transactions
- View existing categories
- View own reports

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

```bash
flake8
black .
```

### Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Deployment

See `PROJECT_DESIGN.md` for detailed deployment instructions.

## License

MIT License

## Author

Generated with advanced OOP patterns and modern Python features.

