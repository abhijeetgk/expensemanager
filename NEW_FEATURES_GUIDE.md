# 🎉 New Features Guide - Expense Manager

## Overview

This guide covers all the exciting new features added to the Expense Manager application to enhance user experience and functionality.

---

## 🎯 Feature 1: Budget Tracking & Alerts

### Description
Comprehensive budget management system with real-time tracking, alerts, and forecasting capabilities.

### Key Features

#### 1. **Budget Creation**
- Create budgets for specific expense categories
- Set budget periods: Weekly, Monthly, Quarterly, or Yearly
- Custom date ranges for flexible budget planning
- Rollover unused amounts to next period (optional)

#### 2. **Budget Tracking**
- Real-time spending vs budget comparison
- Visual progress bars showing utilization percentage
- Color-coded status indicators:
  - 🟢 Green: On track (< 60%)
  - 🔵 Blue: Moderate (60-80%)
  - 🟠 Orange: Near limit (80-100%)
  - 🔴 Red: Exceeded (> 100%)

#### 3. **Smart Alerts**
- Automatic alerts at 80% utilization
- Budget exceeded notifications
- Email alerts (configurable)
- In-app notification center
- Alert history tracking

#### 4. **Budget Analytics**
- Budget summary dashboard
- Utilization percentage tracking
- Remaining days in budget period
- Historical budget performance
- Budget forecasting based on spending patterns

### API Endpoints

#### Budget Management
```
GET    /api/budgets/                    - List all budgets
POST   /api/budgets/                    - Create new budget
GET    /api/budgets/{id}/               - Get budget details
PUT    /api/budgets/{id}/               - Update budget
DELETE /api/budgets/{id}/               - Delete budget
GET    /api/budgets/current/            - Get current active budgets
GET    /api/budgets/summary/            - Get budget summary
GET    /api/budgets/forecast/           - Get budget forecast
POST   /api/budgets/create_recurring/   - Create recurring budgets
POST   /api/budgets/{id}/reset_alerts/  - Reset alert flags
```

#### Budget Alerts
```
GET    /api/budget-alerts/              - List all alerts
GET    /api/budget-alerts/unread/       - Get unread alerts
POST   /api/budget-alerts/mark_read/    - Mark alerts as read
POST   /api/budget-alerts/{id}/mark_read_single/ - Mark single alert as read
```

### Web Interface

#### Budget Dashboard (`/budgets/`)
- Overview cards showing total budget, spent, remaining, and utilization
- Budget cards with progress visualization
- Alert notifications section
- Quick budget creation modal

#### Usage Example

```python
# Create a monthly budget
POST /api/budgets/
{
    "name": "Food Budget - January 2025",
    "category": "food-category-id",
    "amount": "15000.00",
    "period": "MONTHLY",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "alert_threshold_80": true,
    "alert_threshold_100": true
}
```

### Database Models

#### Budget
- `user`: Owner of the budget
- `category`: Expense category
- `name`: Budget name
- `amount`: Budget limit
- `period`: Budget period (WEEKLY/MONTHLY/QUARTERLY/YEARLY)
- `start_date` & `end_date`: Budget period
- `status`: ACTIVE/INACTIVE/EXCEEDED/COMPLETED
- Alert thresholds and flags

#### BudgetAlert
- `budget`: Related budget
- `user`: Alert recipient
- `alert_type`: 80_PERCENT/EXCEEDED/CUSTOM
- `message`: Alert content
- `is_read`: Read status

---

## 👥 Feature 2: Split & Shared Expenses

### Description
Comprehensive expense splitting and debt tracking system for groups, roommates, trips, and shared expenses.

### Key Features

#### 1. **Expense Groups**
- Create groups for different contexts (roommates, trips, projects)
- Add multiple members to groups
- Group admin management
- Custom icons and colors
- Balance summary for all members

#### 2. **Shared Expenses**
- Link expenses to groups
- Track who paid for the expense
- Multiple split methods:
  - **Equal Split**: Divide equally among members
  - **Exact Amounts**: Specify exact amount per person
  - **By Percentage**: Split by percentage
  - **By Shares**: Split by shares/units

#### 3. **Debt Tracking**
- Automatic debt creation from expense splits
- Track who owes whom
- Payment recording with history
- Partial payment support
- Settlement status tracking
- Due date reminders
- Overdue debt detection

#### 4. **Settlement System**
- Add payments towards debts
- Full settlement option
- Payment reference tracking
- Settlement notes
- Payment method recording

### API Endpoints

#### Expense Groups
```
GET    /api/expense-groups/                      - List groups
POST   /api/expense-groups/                      - Create group
GET    /api/expense-groups/{id}/                 - Get group details
PUT    /api/expense-groups/{id}/                 - Update group
DELETE /api/expense-groups/{id}/                 - Delete group
GET    /api/expense-groups/{id}/balance_summary/ - Get balance summary
```

#### Shared Expenses
```
GET    /api/shared-expenses/                          - List shared expenses
POST   /api/shared-expenses/                          - Create shared expense
GET    /api/shared-expenses/{id}/                     - Get expense details
PUT    /api/shared-expenses/{id}/                     - Update expense
DELETE /api/shared-expenses/{id}/                     - Delete expense
POST   /api/shared-expenses/{id}/create_equal_splits/ - Create equal splits
```

#### Debt Management
```
GET    /api/debts/                      - List debts
POST   /api/debts/                      - Create debt
GET    /api/debts/{id}/                 - Get debt details
PUT    /api/debts/{id}/                 - Update debt
DELETE /api/debts/{id}/                 - Delete debt
GET    /api/debts/my_debts/             - Get debts I owe
GET    /api/debts/owed_to_me/           - Get debts owed to me
POST   /api/debts/{id}/add_payment/     - Add payment
POST   /api/debts/{id}/settle/          - Settle debt in full
```

### Usage Example

```python
# 1. Create an expense group
POST /api/expense-groups/
{
    "name": "Apartment Roommates",
    "description": "Shared expenses for apartment",
    "members": ["user1-id", "user2-id", "user3-id"],
    "icon": "fas fa-home",
    "color": "#3B82F6"
}

# 2. Create a shared expense
POST /api/shared-expenses/
{
    "expense": "expense-id",
    "group": "group-id",
    "paid_by": "user1-id",
    "split_method": "EQUAL",
    "notes": "Monthly rent payment"
}

# 3. Create equal splits
POST /api/shared-expenses/{id}/create_equal_splits/
{
    "members": ["user1-id", "user2-id", "user3-id"]
}

# 4. Add payment towards debt
POST /api/debts/{debt-id}/add_payment/
{
    "amount": "500.00",
    "notes": "Partial payment for rent"
}
```

### Database Models

#### ExpenseGroup
- Group management with members
- Admin user
- Balance tracking

#### SharedExpense
- Links expense to group
- Tracks payer
- Split method

#### SharedExpenseSplit
- Individual split amounts
- Settlement status
- Per-person tracking

#### Debt
- Creditor and debtor
- Amount tracking
- Payment history
- Status management

#### DebtPayment
- Payment records
- Reference numbers
- Payment methods

---

## 📱 Feature 3: Mobile-First Enhancements

### Description
Modern, mobile-friendly UI enhancements including dark mode, floating action buttons, and responsive design improvements.

### Key Features

#### 1. **Dark Mode**
- 🌙 Toggle between light and dark themes
- Persistent theme preference (localStorage)
- Smooth transitions
- Optimized color scheme for both modes
- Custom CSS variables for easy theming

**Colors:**
- **Light Mode**: White backgrounds, dark text
- **Dark Mode**: Dark gray backgrounds, light text
- Consistent accent colors across themes

**Toggle Button:**
- Fixed position (bottom-left)
- Moon icon in light mode
- Sun icon in dark mode
- Smooth hover effects

#### 2. **Floating Action Button (FAB)**
- 🎯 Quick access to common actions
- Fixed position (bottom-right)
- Expandable menu with:
  - Add Income (green)
  - Add Expense (red)
- Smooth animations
- Click outside to close
- Mobile-responsive sizing

**Features:**
- Gradient background
- Rotation animation on hover
- Slide-out menu items
- Touch-friendly on mobile

#### 3. **Responsive Design**
- Mobile-first approach
- Optimized for tablets and phones
- Collapsible navigation
- Touch-friendly buttons
- Responsive typography
- Fluid layouts

**Breakpoints:**
- Desktop: > 768px
- Tablet: 768px
- Mobile: < 768px

#### 4. **UI Improvements**
- Card-based layouts
- Color-coded status indicators
- Progress bars with labels
- Icon-rich interface
- Loading animations
- Hover effects
- Smooth transitions

### Implementation

#### Dark Mode
```javascript
// Toggle dark mode
const darkModeToggle = document.getElementById('darkModeToggle');
darkModeToggle.addEventListener('click', function() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});
```

#### CSS Variables
```css
:root {
    --primary-color: #4F46E5;
    --light-bg: #F9FAFB;
    --text-color: #1F2937;
    --card-bg: #FFFFFF;
}

[data-theme="dark"] {
    --light-bg: #111827;
    --text-color: #F9FAFB;
    --card-bg: #1F2937;
}
```

---

## 🚀 Getting Started

### Installation

1. **Update Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run Migrations**
```bash
python manage.py migrate
```

3. **Create Sample Data (Optional)**
```bash
python manage.py create_sample_data
```

4. **Start Server**
```bash
python manage.py runserver
```

### Accessing New Features

#### Web Interface
- **Budget Management**: http://localhost:8000/budgets/
- **Dashboard**: http://localhost:8000/ (updated with new features)
- **Dark Mode**: Click moon/sun icon (bottom-left)
- **Quick Add**: Click FAB button (bottom-right)

#### API Access
All new endpoints are available at:
- Budget API: `/api/budgets/`
- Shared Expenses API: `/api/expense-groups/`, `/api/shared-expenses/`, `/api/debgets/`

---

## 📊 Usage Examples

### Example 1: Monthly Budget Setup

```python
# 1. Create category-wise budgets for the month
budgets = [
    {"category": "food", "amount": 15000, "name": "Food & Dining"},
    {"category": "transport", "amount": 5000, "name": "Transportation"},
    {"category": "utilities", "amount": 3000, "name": "Utilities"},
    {"category": "entertainment", "amount": 2000, "name": "Entertainment"}
]

for budget in budgets:
    POST /api/budgets/
    {
        "name": f"{budget['name']} - January 2025",
        "category": budget["category"],
        "amount": budget["amount"],
        "period": "MONTHLY",
        "start_date": "2025-01-01",
        "end_date": "2025-01-31"
    }
```

### Example 2: Splitting Trip Expenses

```python
# 1. Create trip group
POST /api/expense-groups/
{
    "name": "Goa Trip 2025",
    "description": "Beach vacation expenses",
    "members": ["alice-id", "bob-id", "charlie-id"]
}

# 2. Add hotel expense
POST /api/transactions/expense/
{
    "amount": 9000,
    "description": "Hotel accommodation",
    "category": "travel",
    ...
}

# 3. Create shared expense
POST /api/shared-expenses/
{
    "expense": "expense-id",
    "group": "trip-group-id",
    "paid_by": "alice-id",
    "split_method": "EQUAL"
}

# 4. Auto-split equally
POST /api/shared-expenses/{id}/create_equal_splits/
```

### Example 3: Settling Debts

```python
# 1. Check my debts
GET /api/debts/my_debts/

# 2. Add payment
POST /api/debts/{debt-id}/add_payment/
{
    "amount": 1000,
    "payment_method": "MOBILE_PAYMENT",
    "reference_number": "TXN123456",
    "notes": "Partial payment via UPI"
}

# 3. Settle remaining amount
POST /api/debts/{debt-id}/settle/
{
    "notes": "Final settlement"
}
```

---

## 🎨 UI/UX Highlights

### Visual Design
- Modern gradient navbar
- Card-based layouts with shadows
- Color-coded status indicators
- Icon-rich interface
- Progress bars with percentages
- Smooth animations

### Color Scheme
- **Primary**: Indigo (#4F46E5)
- **Success**: Green (#10B981)
- **Danger**: Red (#EF4444)
- **Warning**: Orange (#F59E0B)
- **Info**: Blue (#3B82F6)

### Typography
- Font: Inter, system fonts
- Clear hierarchy
- Readable sizes
- Bold for emphasis

### Interactions
- Hover effects
- Click feedback
- Loading states
- Error handling
- Success messages

---

## 🔧 Configuration

### Email Notifications
Configure in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Expense Manager <your-email@gmail.com>'
```

### Budget Alert Settings
- 80% threshold: Enabled by default
- 100% threshold: Enabled by default
- Email alerts: Based on user profile settings

---

## 📈 Best Practices

### Budget Management
1. Set realistic budget amounts based on historical spending
2. Use budget forecasting to plan future budgets
3. Review budget utilization regularly
4. Adjust budgets based on changing needs

### Expense Splitting
1. Create groups for different contexts
2. Always specify who paid for shared expenses
3. Settle debts promptly
4. Keep payment references for tracking

### Mobile Usage
1. Enable dark mode for nighttime use
2. Use FAB for quick expense entry
3. Take advantage of mobile-optimized layouts
4. Use touch-friendly controls

---

## 🐛 Troubleshooting

### Budget Alerts Not Sending
- Check email configuration
- Verify user profile has email notifications enabled
- Check alert threshold settings

### Shared Expense Splits Not Creating
- Ensure group has members
- Verify expense is completed
- Check split method is valid

### Dark Mode Not Persisting
- Clear browser localStorage
- Try different browser
- Check JavaScript console for errors

---

## 🎯 Future Enhancements

Potential features for future releases:
- Multi-currency support for budgets
- Budget templates
- Expense split by percentage
- Group expense analytics
- Bill scanning (OCR)
- Expense categories auto-suggestion
- Budget vs actual charts
- Expense forecasting
- Social features (expense feed)
- Mobile app companion

---

## 📝 API Quick Reference

### Budget API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/budgets/` | List budgets |
| POST | `/api/budgets/` | Create budget |
| GET | `/api/budgets/summary/` | Budget summary |
| GET | `/api/budgets/forecast/` | Budget forecast |

### Shared Expenses API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/expense-groups/` | List groups |
| POST | `/api/shared-expenses/` | Create shared expense |
| GET | `/api/debts/my_debts/` | My debts |
| POST | `/api/debts/{id}/add_payment/` | Add payment |

---

## 👥 Contributing

To contribute to these features:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🎉 Changelog

### Version 2.0.0 (2025-01-15)
- ✨ Added Budget Tracking & Alerts
- ✨ Added Split & Shared Expenses
- ✨ Added Dark Mode
- ✨ Added Floating Action Button
- 🎨 Improved Mobile Responsiveness
- 📱 Enhanced UI/UX

---

**Enjoy the new features! 🚀**

