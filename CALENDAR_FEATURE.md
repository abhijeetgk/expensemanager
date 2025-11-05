# 📅 Calendar View Feature

## Overview

The Calendar View provides an interactive, visual way to see all your income and expense transactions displayed on a calendar. This makes it easy to track your financial activity over time and identify spending patterns.

## Features

### 1. **Interactive Calendar Display**
- Full calendar view powered by FullCalendar.js
- Color-coded transactions:
  - 💰 **Green** - Income transactions
  - 💸 **Red** - Expense transactions
- Hover to see transaction details
- Click on transactions for full details

### 2. **Multiple View Modes**
Switch between different calendar views:
- **Month View** - See the entire month at a glance (default)
- **Week View** - Focus on a single week with time slots
- **Day View** - Detailed view of a single day
- **List View** - List format of all transactions

### 3. **Monthly Summary Cards**
Real-time summary at the top of the page:
- **Total Income** - Sum of all income for the visible month
- **Total Expenses** - Sum of all expenses for the visible month
- **Net Balance** - Income minus expenses

### 4. **Transaction Details Modal**
Click any transaction to see:
- Amount
- Category
- Description
- Source/Vendor
- Payment method (for expenses)
- Date
- **Edit button** - Quick access to edit the transaction

### 5. **Quick Add Functionality**
- Click on any date to quickly add a transaction for that day
- Quick add buttons at the top (Add Income / Add Expense)
- Date is automatically populated when adding from calendar

### 6. **Navigation Controls**
- Previous/Next month arrows
- "Today" button to jump to current date
- Month/Year title showing current view

### 7. **Responsive Design**
- Works beautifully on desktop, tablet, and mobile
- Touch-friendly on mobile devices
- Adapts to screen size

## How to Access

### Web Interface
Navigate to: **http://localhost:8000/calendar/**

Or click **Calendar** in the navigation menu.

## API Endpoints

### Get Calendar Events
```
GET /calendar/api/events/?start=2025-01-01&end=2025-01-31
```

Returns all transactions for the date range in FullCalendar event format.

**Response:**
```json
[
  {
    "id": "income-uuid",
    "title": "💰 Salary: ₹50,000",
    "start": "2025-01-01",
    "backgroundColor": "#10B981",
    "extendedProps": {
      "type": "income",
      "amount": 50000.00,
      "description": "Monthly salary",
      "category": "Salary",
      "source": "Company ABC"
    }
  },
  {
    "id": "expense-uuid",
    "title": "💸 Food: ₹500",
    "start": "2025-01-05",
    "backgroundColor": "#EF4444",
    "extendedProps": {
      "type": "expense",
      "amount": 500.00,
      "description": "Groceries",
      "category": "Food",
      "vendor": "Supermarket"
    }
  }
]
```

### Get Day Summary
```
GET /calendar/api/day-summary/?date=2025-01-15
```

Returns aggregated data for a specific day.

**Response:**
```json
{
  "date": "2025-01-15",
  "income_total": 5000.00,
  "expense_total": 1500.00,
  "net_balance": 3500.00,
  "income_transactions": [...],
  "expense_transactions": [...]
}
```

### Get Month Summary
```
GET /calendar/api/month-summary/?year=2025&month=1
```

Returns aggregated data for a specific month.

**Response:**
```json
{
  "year": 2025,
  "month": 1,
  "income_total": 50000.00,
  "expense_total": 25000.00,
  "net_balance": 25000.00,
  "income_by_category": [
    {"category__name": "Salary", "total": 45000.00},
    {"category__name": "Freelance", "total": 5000.00}
  ],
  "expense_by_category": [
    {"category__name": "Rent", "total": 15000.00},
    {"category__name": "Food", "total": 5000.00}
  ],
  "daily_data": [
    {
      "date": "2025-01-01",
      "income": 50000.00,
      "expense": 0,
      "net": 50000.00
    }
  ]
}
```

## Usage Examples

### Example 1: View Monthly Transactions
1. Navigate to **Calendar** from the menu
2. See all your transactions displayed on the calendar
3. Use prev/next arrows to switch months
4. Summary cards update automatically

### Example 2: Check Transaction Details
1. Click on any colored event on the calendar
2. Modal popup shows full transaction details
3. Click **Edit** button to modify the transaction

### Example 3: Quick Add Transaction
1. Click on any empty date on the calendar
2. Confirm the date in the popup
3. Add transaction form opens with date pre-filled

### Example 4: Switch View Modes
1. Click the view toggle buttons at the top
2. Choose between Month, Week, Day, or List view
3. Calendar updates instantly

### Example 5: Find Spending Pattern
1. Look at the calendar overview
2. Identify days with many red (expense) events
3. Click on those days to see what was spent
4. Use this to plan future budgets

## Technical Details

### Frontend
- **Library**: FullCalendar.js v6.1.9
- **Event rendering**: Dynamic with AJAX calls
- **Interactions**: Click, hover, date select
- **Responsive**: Mobile-first design

### Backend
- **Views**: Django function-based views
- **Data**: Aggregated from Income and Expense models
- **Filtering**: Date-based with timezone awareness
- **Format**: JSON responses for AJAX

### Styling
- Matches dark mode theme
- Color-coded by transaction type
- Card-based summary design
- Smooth animations

## Color Scheme

| Transaction Type | Color | Hex Code |
|-----------------|-------|----------|
| Income | Green | #10B981 |
| Expense | Red | #EF4444 |
| Today | Blue tint | #4F46E5 (10% opacity) |

## Benefits

### 1. **Visual Overview**
See your entire month's transactions at a glance, making it easy to identify patterns and trends.

### 2. **Better Planning**
Quickly see which days have high expenses and plan accordingly for upcoming dates.

### 3. **Quick Access**
Click any date to add transactions or view existing ones with minimal clicks.

### 4. **Pattern Recognition**
Identify spending patterns by visual cues:
- Many red events = high spending day
- Green events = income received
- Empty days = no transactions

### 5. **Monthly Insights**
Summary cards provide instant insights into:
- How much you earned
- How much you spent
- Your net savings

## Mobile Experience

### Touch-Friendly
- Large touch targets for dates
- Swipe to navigate months
- Tap events for details
- Responsive modal dialogs

### Optimized Layout
- Summary cards stack vertically
- View toggles remain accessible
- Calendar adapts to screen width
- Scrollable on small screens

## Tips & Tricks

### 💡 Tip 1: Quick Navigation
Press the **Today** button to instantly jump to the current date, no matter which month you're viewing.

### 💡 Tip 2: Bulk View
Use **List View** to see all transactions in a chronological list format, great for reviewing or exporting.

### 💡 Tip 3: Pattern Analysis
Look for clusters of expense events (red) to identify your high-spending periods and adjust budgets accordingly.

### 💡 Tip 4: Quick Entry
Click on future dates to pre-plan and add upcoming bills or expected income.

### 💡 Tip 5: Summary Tracking
Watch the summary cards change as you navigate months to track your financial trends over time.

## Integration with Other Features

### Works With Budgets
- See if you're staying within budget by viewing expense density on the calendar
- Use budget alerts alongside calendar view for complete control

### Works With Reports
- Calendar provides visual context
- Reports provide detailed analysis
- Use both for comprehensive insights

### Works With Categories
- Transactions show category names in event titles
- Easy to see which categories appear most frequently

## Future Enhancements

Potential features for future releases:
- Drag-and-drop to reschedule transactions
- Color coding by category
- Recurring transaction preview (show future occurrences)
- Mini calendar widget on dashboard
- Export calendar view to PDF
- Share calendar view with family members
- Budget indicators on calendar dates
- Bill due date reminders on calendar

## Troubleshooting

### Calendar Not Loading
- Check your internet connection (FullCalendar loads from CDN)
- Clear browser cache
- Check browser console for errors

### Transactions Not Showing
- Verify transactions exist in the database
- Check date range is correct
- Refresh the page
- Check browser console for API errors

### Summary Cards Not Updating
- Check API endpoint is responding
- Verify network connection
- Check browser console for errors

## Browser Compatibility

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

**Enjoy visualizing your financial data with the Calendar View! 📅✨**

