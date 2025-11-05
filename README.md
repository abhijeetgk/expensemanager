# Expense Manager

A comprehensive Django-based expense management system with role-based access control, real-time reporting, and advanced analytics.

## Features

### Core Features
- **User Management**: Multi-role user system (Admin, Power User, User)
- **Category Management**: Dynamic income and expense categories
- **Transaction Tracking**: Detailed income and expense entries
- **Advanced Reporting**: Month-wise, category-wise, and period-based reports
- **Data Export**: Export reports to Excel and PDF
- **Admin Dashboard**: Rich UI with charts and widgets
- **RESTful API**: Complete API for all operations
- **Role-Based Permissions**: Granular access control

### 🎉 New Features (v2.0+)
- **💰 Budget Tracking & Alerts**: Set budgets, track spending, get automatic alerts at 80% and 100% utilization
- **👥 Split & Shared Expenses**: Create expense groups, split bills, track debts, and settle payments
- **📅 Calendar View**: Interactive calendar to visualize all transactions with color-coded events
- **🤖 AI Assistant**: Add transactions using natural language - just type "add income of rs 10000 under salary on 03 nov 25"
- **🌙 Dark Mode**: Toggle between light and dark themes with persistent preference
- **📱 Floating Action Button**: Quick access to add income/expense from any page
- **📱 Mobile-First Design**: Enhanced responsive design for mobile devices

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
├── config/                   # Project configuration
├── apps/
│   ├── accounts/            # User management
│   ├── categories/          # Category management
│   ├── transactions/        # Income & Expense transactions
│   ├── reports/             # Reporting & Analytics
│   ├── dashboard/           # Admin dashboard
│   ├── budgets/            # 💰 Budget tracking & alerts (NEW)
│   ├── shared_expenses/    # 👥 Split expenses & debt tracking (NEW)
│   └── core/               # Shared utilities
├── static/                  # Static files
├── media/                   # User uploads
└── templates/              # HTML templates
    └── web/
        ├── budgets.html    # 💰 Budget management page (NEW)
        └── ...
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

### 💰 Budgets (NEW)
- `GET /api/budgets/` - List all budgets
- `POST /api/budgets/` - Create budget
- `GET /api/budgets/current/` - Get current budgets
- `GET /api/budgets/summary/` - Budget summary
- `GET /api/budgets/forecast/` - Budget forecast
- `GET /api/budget-alerts/unread/` - Get unread alerts

### 👥 Shared Expenses (NEW)
- `GET /api/expense-groups/` - List expense groups
- `POST /api/expense-groups/` - Create group
- `GET /api/shared-expenses/` - List shared expenses
- `POST /api/shared-expenses/` - Create shared expense
- `GET /api/debts/my_debts/` - Get my debts
- `GET /api/debts/owed_to_me/` - Get debts owed to me
- `POST /api/debts/{id}/add_payment/` - Add payment

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

## 📚 Documentation

- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[New Features Guide](NEW_FEATURES_GUIDE.md)** - Detailed guide for v2.0 features
- **[Calendar Feature Guide](CALENDAR_FEATURE.md)** - Interactive calendar documentation
- **[AI Assistant Guide](AI_ASSISTANT_GUIDE.md)** - Natural language transaction entry
- **[Web Interface Guide](WEB_INTERFACE_GUIDE.md)** - User interface documentation
- **[Project Design](PROJECT_DESIGN.md)** - Technical architecture
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment

## 🎯 Quick Start with New Features

### Budget Tracking
```bash
# Access budget management
http://localhost:8000/budgets/

# Or via API
curl -X POST http://localhost:8000/api/budgets/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"category": "food-id", "amount": 15000, "period": "MONTHLY"}'
```

### Split Expenses
```python
# Create expense group
POST /api/expense-groups/
{
    "name": "Roommates",
    "members": ["user1-id", "user2-id"]
}

# Create shared expense and split equally
POST /api/shared-expenses/
POST /api/shared-expenses/{id}/create_equal_splits/
```

### Calendar View
```bash
# Access interactive calendar
http://localhost:8000/calendar/

# Features:
# - Visual transaction overview
# - Month/Week/Day/List views
# - Click events for details
# - Click dates to add transactions
```

### AI Assistant - Natural Language Entry
```bash
# Access AI chat assistant
http://localhost:8000/ai-assistant/chat/

# Just type naturally:
"Add income of rs 10000 under salary on 03 nov 25"
"Spent 500 on groceries yesterday"
"Paid 2000 for electricity today"

# The AI will:
# - Parse your input automatically
# - Ask for missing information
# - Confirm before adding
# - Create the transaction instantly
```

### Dark Mode & FAB
- **Dark Mode**: Click the moon/sun icon (bottom-left corner)
- **Quick Add**: Click the + button (bottom-right corner)
- Both features work automatically on all pages!

## License

MIT License

## Author

Built with advanced OOP patterns, modern Python features, and user-centric design.

