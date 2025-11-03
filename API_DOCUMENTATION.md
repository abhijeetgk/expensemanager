# Expense Manager API Documentation

## Overview

The Expense Manager API provides RESTful endpoints for managing users, categories, transactions, reports, and dashboards. All endpoints require authentication via JWT tokens except for the login endpoint.

## Base URL

```
http://localhost:8000/api
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Get Access Token

**Endpoint:** `POST /auth/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token

**Endpoint:** `POST /auth/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using the Access Token

Include the access token in the Authorization header for all requests:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## User Management

### Get Current User

**Endpoint:** `GET /accounts/users/me/`

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "user",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "role": "USER",
  "is_active": true,
  "permissions": {
    "can_manage_users": false,
    "can_manage_categories": false,
    "can_create_categories": false
  }
}
```

### List Users (Admin Only)

**Endpoint:** `GET /accounts/users/`

**Query Parameters:**
- `role`: Filter by role (ADMIN, POWER_USER, USER)
- `is_active`: Filter by active status (true/false)
- `search`: Search by email, username, or name

### Create User (Admin Only)

**Endpoint:** `POST /accounts/users/`

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "USER"
}
```

### Update User Role (Admin Only)

**Endpoint:** `POST /accounts/users/{id}/change_role/`

**Request Body:**
```json
{
  "role": "POWER_USER"
}
```

### Toggle User Status (Admin Only)

**Endpoint:** `POST /accounts/users/{id}/toggle_status/`

## Category Management

### List Income Categories

**Endpoint:** `GET /categories/income/`

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": "uuid",
      "name": "Salary",
      "description": "Monthly salary",
      "icon": "fas fa-briefcase",
      "color": "#10B981",
      "is_active": true,
      "is_recurring": true,
      "tax_applicable": true
    }
  ]
}
```

### List Expense Categories

**Endpoint:** `GET /categories/expense/`

### Create Category (Admin Only)

**Endpoint:** `POST /categories/income/` or `POST /categories/expense/`

**Request Body (Income):**
```json
{
  "name": "Freelance",
  "description": "Freelance income",
  "icon": "fas fa-laptop",
  "color": "#3B82F6",
  "is_recurring": false,
  "tax_applicable": true
}
```

**Request Body (Expense):**
```json
{
  "name": "Food",
  "description": "Food and dining",
  "icon": "fas fa-utensils",
  "color": "#EF4444",
  "budget_limit": "500.00",
  "is_essential": true
}
```

### Quick Create Category (Power User)

**Endpoint:** `POST /categories/income/quick_create/` or `POST /categories/expense/quick_create/`

**Request Body:**
```json
{
  "name": "New Category",
  "description": "Quick category",
  "color": "#3B82F6"
}
```

## Transaction Management

### List Income Transactions

**Endpoint:** `GET /transactions/income/`

**Query Parameters:**
- `category`: Filter by category ID
- `status`: Filter by status (PENDING, COMPLETED, CANCELLED)
- `start_date`: Filter by start date (YYYY-MM-DD)
- `end_date`: Filter by end date (YYYY-MM-DD)
- `search`: Search in description, source, reference number

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": "uuid",
      "amount": "5000.00",
      "description": "Monthly salary",
      "transaction_date": "2025-01-15",
      "status": "COMPLETED",
      "category": "uuid",
      "category_detail": {
        "name": "Salary",
        "color": "#10B981"
      },
      "source": "Company ABC",
      "net_amount": "4500.00",
      "tax_amount": "500.00",
      "formatted_amount": "$5,000.00"
    }
  ]
}
```

### Create Income Transaction

**Endpoint:** `POST /transactions/income/`

**Request Body:**
```json
{
  "amount": "5000.00",
  "description": "Monthly salary",
  "transaction_date": "2025-01-15",
  "category": "category-uuid",
  "source": "Company ABC",
  "is_recurring": true,
  "recurrence_period": "MONTHLY",
  "tax_amount": "500.00"
}
```

### List Expense Transactions

**Endpoint:** `GET /transactions/expense/`

**Query Parameters:**
- `category`: Filter by category ID
- `status`: Filter by status
- `payment_method`: Filter by payment method
- `is_reimbursable`: Filter by reimbursable status

### Create Expense Transaction

**Endpoint:** `POST /transactions/expense/`

**Request Body:**
```json
{
  "amount": "50.00",
  "description": "Lunch at restaurant",
  "transaction_date": "2025-01-15",
  "category": "category-uuid",
  "payment_method": "CREDIT_CARD",
  "vendor": "Restaurant XYZ",
  "location": "Downtown",
  "is_reimbursable": false
}
```

### Transaction Actions

**Mark as Completed:** `POST /transactions/income/{id}/complete/` or `POST /transactions/expense/{id}/complete/`

**Cancel Transaction:** `POST /transactions/income/{id}/cancel/`
```json
{
  "reason": "Duplicate entry"
}
```

**Mark as Reimbursed:** `POST /transactions/expense/{id}/mark_reimbursed/`

**Add Tag:** `POST /transactions/income/{id}/add_tag/` or `POST /transactions/expense/{id}/add_tag/`
```json
{
  "tag": "important"
}
```

## Reports & Analytics

### Summary Report

**Endpoint:** `GET /reports/summary/`

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)

**Response:**
```json
{
  "total_income": 15000.00,
  "total_expense": 8000.00,
  "net_balance": 7000.00,
  "transaction_count": 45,
  "period_start": "2025-01-01",
  "period_end": "2025-01-31",
  "details": {
    "income_count": 10,
    "expense_count": 35,
    "average_income": 1500.00,
    "average_expense": 228.57
  }
}
```

### Monthly Report

**Endpoint:** `GET /reports/monthly/`

**Query Parameters:**
- `year`: Year (default: current year)
- `month`: Month (default: current month)

### Category-wise Report

**Endpoint:** `GET /reports/category-wise/`

**Query Parameters:**
- `type`: Transaction type (INCOME or EXPENSE)
- `start_date`: Start date
- `end_date`: End date

**Response:**
```json
{
  "transaction_type": "EXPENSE",
  "categories": [
    {
      "category_name": "Food & Dining",
      "category_id": "uuid",
      "total_amount": 1500.00,
      "transaction_count": 25,
      "percentage": 35.5,
      "color": "#EF4444"
    }
  ]
}
```

### Trend Analysis

**Endpoint:** `GET /reports/trend-analysis/`

**Query Parameters:**
- `months`: Number of months (default: 6)

### Budget Analysis

**Endpoint:** `GET /reports/budget-analysis/`

**Query Parameters:**
- `month`: Month (default: current month)
- `year`: Year (default: current year)

**Response:**
```json
{
  "budget_analysis": [
    {
      "category_id": "uuid",
      "category_name": "Food & Dining",
      "budget_limit": 500.00,
      "total_spent": 450.00,
      "remaining": 50.00,
      "utilization_percentage": 90.0,
      "is_over_budget": false,
      "color": "#EF4444"
    }
  ]
}
```

### Export Reports

**Export to Excel:** `POST /reports/export/excel/`

**Export to PDF:** `POST /reports/export/pdf/`

**Request Body:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

**Response:** File download

## Dashboard (Admin)

### Dashboard Statistics

**Endpoint:** `GET /dashboard/stats/`

**Response:**
```json
{
  "users": {
    "total": 25,
    "active": 22,
    "new_this_month": 3
  },
  "categories": {
    "income": 5,
    "expense": 8,
    "total": 13
  },
  "transactions": {
    "total_count": 500,
    "total_income": 75000.00,
    "total_expense": 45000.00,
    "net_balance": 30000.00
  },
  "current_month": {
    "income": 15000.00,
    "expense": 8000.00,
    "net": 7000.00
  }
}
```

### Income vs Expense Chart

**Endpoint:** `GET /dashboard/charts/income-expense/`

**Query Parameters:**
- `months`: Number of months (default: 6)

### Category Breakdown Chart

**Endpoint:** `GET /dashboard/charts/category-breakdown/`

**Query Parameters:**
- `type`: Transaction type (income or expense)
- `period`: Period (month, quarter, year)

### User Dashboard Statistics

**Endpoint:** `GET /dashboard/user/stats/`

**Response:**
```json
{
  "current_month": {
    "income": 5000.00,
    "expense": 2500.00,
    "net": 2500.00,
    "savings_rate": 50.0
  },
  "overall": {
    "total_income": 60000.00,
    "total_expense": 35000.00,
    "net_balance": 25000.00
  },
  "transactions": {
    "income_count": 12,
    "expense_count": 85,
    "total_count": 97
  },
  "pending_reimbursement": 350.00
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse. Default limits:
- Authenticated users: 1000 requests/hour
- Anonymous users: 100 requests/hour

## Pagination

List endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Paginated Response Format:**
```json
{
  "count": 100,
  "next": "http://api.example.com/endpoint/?page=2",
  "previous": null,
  "results": []
}
```

## Filtering and Sorting

Most list endpoints support:
- **Filtering:** Use query parameters matching field names
- **Search:** Use `search` parameter
- **Ordering:** Use `ordering` parameter (prefix with `-` for descending)

**Example:**
```
GET /transactions/expense/?category=uuid&ordering=-transaction_date&search=restaurant
```

