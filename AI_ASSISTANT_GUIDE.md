# 🤖 AI Assistant - Natural Language Transaction Entry

## Overview

The AI Assistant allows you to add income and expense transactions using natural language - just type what you want to add in plain English! No more filling out forms or selecting from dropdowns.

## Features

### 1. **Natural Language Processing**
Simply describe your transaction in plain English:
- "Add income of ₹50000 under salary today"
- "Spent ₹500 on groceries yesterday"
- "Paid ₹2000 for electricity on 15th"
- "Add expense of rs 1500 under transport"

### 2. **Intelligent Parsing**
The AI automatically extracts:
- **Transaction Type** (income or expense)
- **Amount** (supports ₹, rs, rupees, $)
- **Category** (automatically detects common categories)
- **Date** (supports today, yesterday, dates like "03 nov 25")
- **Description** (additional details)
- **Payment Method** (for expenses)
- **Source** (for income)

### 3. **Conversational Interface**
If information is missing, the bot will ask:
- "Is this an income or expense?"
- "How much is the amount?"
- "What category?"

### 4. **Smart Confirmation**
Before adding, you'll see a confirmation with all details:
- Amount
- Category
- Date
- Additional notes

### 5. **Real-time Processing**
- Instant parsing
- Quick responses
- Smooth chat experience
- Typing indicators

## How to Use

### Access the AI Assistant

1. **From Navigation**: Click "AI Assistant" in the navigation menu
2. **Direct URL**: `http://localhost:8000/ai-assistant/chat/`

### Adding Transactions

#### Example 1: Simple Income
**You type:** "Add income of ₹50000 under salary today"

**AI Response:** "✅ Ready to add this income:
- Amount: ₹50,000.00
- Category: Salary  
- Date: November 5, 2025

[Confirm & Add] [Cancel]"

#### Example 2: Expense with Date
**You type:** "Spent 500 rupees on food yesterday"

**AI Response:** "✅ Ready to add this expense:
- Amount: ₹500.00
- Category: Food
- Date: November 4, 2025

[Confirm & Add] [Cancel]"

#### Example 3: Incomplete Information
**You type:** "Paid 2000 for electricity"

**AI Response:** "What date was this transaction?"

**You type:** "On the 15th"

**AI Response:** Confirmation with all details

### Supported Date Formats

1. **Relative Dates**
   - "today"
   - "yesterday"
   - "tomorrow"

2. **Explicit Dates**
   - "03 nov 25"
   - "3 november 2025"
   - "15th" (current month assumed)
   - "nov 03 25"
   - "2025-11-03"
   - "03-11-2025"

### Supported Amount Formats

- `₹1000`
- `rs 1000`
- `rs. 1000`
- `1000 rupees`
- `1000 rs`
- `$1000`
- `1,50,000` (with commas)
- `1000.50` (with decimals)

### Recognized Categories

#### Income Categories
- Salary / Wage / Paycheck
- Freelance / Contract / Consulting
- Investment / Returns
- Gift / Bonus

#### Expense Categories
- Food / Groceries / Restaurant / Lunch / Dinner
- Transport / Fuel / Gas / Uber / Taxi
- Utilities / Electricity / Water / Internet / Phone
- Rent / Lease / Housing
- Entertainment / Movie / Netflix / Spotify
- Shopping / Clothes / Fashion
- Healthcare / Medical / Doctor / Medicine
- Education / Course / Training / Tuition

### Keywords for Transaction Types

#### Income Keywords
- income, received, got, earned, salary, payment, credit

#### Expense Keywords  
- expense, spent, paid, bought, purchase, debit, cost

## Natural Language Examples

### ✅ Valid Inputs

```
"Add income of ₹50000 under salary today"
"Spent ₹500 on groceries yesterday"
"Paid 2000 rupees for electricity on 15th"
"Add expense of rs 1500 under transport"
"Received 10000 from freelance project on 03 nov 25"
"Bought clothes for 3000 rs"
"Got salary of 45000 today"
"Paid rent 15000 via bank transfer"
"Spent 250 on lunch at restaurant"
"Add income 5000 under bonus yesterday"
```

### 🔍 What the AI Extracts

From: **"Spent ₹500 on groceries yesterday"**

Extracted:
- Type: expense
- Amount: 500
- Category: groceries → food
- Date: yesterday → 2025-11-04
- Description: "on groceries"

## API Endpoints

### Parse Transaction
```
POST /ai-assistant/api/parse/
```

**Request:**
```json
{
  "message": "add income of rs 10000 under salary on 03 nov 25",
  "context": {}
}
```

**Response:**
```json
{
  "response": {
    "type": "confirmation",
    "message": "I'll add this income...",
    "buttons": ["Confirm", "Edit", "Cancel"]
  },
  "context": {
    "type": "income",
    "amount": 10000,
    "category": "salary",
    "date": "2025-11-03",
    "confidence": 100
  },
  "parsed_data": { ... },
  "ready_to_save": true,
  "confidence": 100
}
```

### Create Transaction
```
POST /ai-assistant/api/create/
```

**Request:**
```json
{
  "type": "income",
  "amount": 10000,
  "category": "salary",
  "date": "2025-11-03",
  "description": "Monthly salary"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Income added successfully!",
  "transaction": {
    "id": "uuid",
    "type": "income",
    "amount": 10000,
    "category": "Salary",
    "date": "2025-11-03"
  }
}
```

## Technical Details

### NLP Parser (`nlp_parser.py`)

**TransactionParser Class**
- Regex-based pattern matching
- Multi-format date parsing
- Amount extraction with currency support
- Category detection from keywords
- Confidence scoring

**ConversationalBot Class**
- Context management
- Missing field detection
- Dynamic question generation
- Confirmation formatting

### Parsing Algorithm

1. **Type Extraction**
   - Search for income/expense keywords
   - Default: None (ask user)

2. **Amount Extraction**
   - Multiple regex patterns for different formats
   - Decimal and comma support
   - Currency symbol detection

3. **Date Extraction**
   - Relative date keywords
   - Explicit date patterns (multiple formats)
   - Fuzzy date parsing with dateutil

4. **Category Extraction**
   - Keyword matching against category database
   - "under X" pattern detection
   - Common synonyms recognition

5. **Confidence Calculation**
   - Based on required fields extracted
   - 100% = all fields found
   - Lower % = missing fields

### UI Components

**Chat Interface**
- Modern chat bubble design
- Bot avatar (robot icon)
- User avatar
- Typing indicators
- Message animations
- Button-based responses

**Features**
- Auto-scroll to latest message
- Enter key to send
- Welcome screen with examples
- Confirmation boxes
- Quick suggestion chips

## Advantages

### ⚡ Speed
- Add transactions in seconds
- No form filling required
- Natural conversation flow

### 🎯 Accuracy
- Smart parsing algorithms
- Confirmation before saving
- Error handling with clarifications

### 🧠 Intelligence
- Learns from common patterns
- Suggests corrections
- Auto-creates categories (if permission)

### 💬 Conversational
- Friendly chat interface
- Asks clarifying questions
- Provides helpful feedback

### 📱 Mobile-Friendly
- Works great on mobile
- Touch-optimized
- Responsive design

## Tips & Best Practices

### 💡 Tip 1: Be Specific
Include all details in one message:
✅ "Add income of ₹50000 under salary today"
❌ "Add income" (will need follow-up questions)

### 💡 Tip 2: Use Common Categories
Stick to recognized category names for best results:
- Salary, Food, Transport, Rent, Utilities, etc.

### 💡 Tip 3: Date Flexibility
The AI understands many date formats:
- "today", "yesterday"
- "15th"
- "03 nov 25"
- "november 3 2025"

### 💡 Tip 4: Amount Formats
Any of these work:
- ₹10000
- rs 10000
- 10000 rupees
- 10,000

### 💡 Tip 5: Review Before Confirming
Always check the confirmation details before clicking "Confirm & Add"

## Limitations & Future Enhancements

### Current Limitations
- English language only
- Pre-defined category list
- No bulk transaction entry
- No attachment support

### Planned Enhancements
- Multi-language support
- Voice input
- Receipt photo parsing (OCR)
- Learning from user patterns
- Custom category suggestions
- Batch transaction processing
- Integration with other features

## Troubleshooting

### Issue: Bot doesn't understand my input
**Solution**: Try being more explicit:
- Include all details (type, amount, category, date)
- Use common keywords
- Check example formats

### Issue: Wrong category detected
**Solution**: 
- Specify category explicitly: "under food"
- Use exact category name from your list

### Issue: Date not parsed correctly
**Solution**:
- Use explicit format: "03 nov 25"
- Or relative: "today", "yesterday"
- Avoid ambiguous formats

### Issue: Amount extracted wrong
**Solution**:
- Include currency symbol: ₹500 or rs 500
- Avoid special characters except comma and decimal

## Examples by Use Case

### Daily Expenses
```
"Spent 50 on tea"
"Lunch cost 200 today"
"Bought vegetables for 300"
"Paid 100 for parking"
```

### Monthly Bills
```
"Paid rent 15000 on 1st"
"Electricity bill 2000 today"
"Internet bill 1000 paid yesterday"
"Mobile recharge 500"
```

### Income Entries
```
"Received salary 50000 today"
"Got freelance payment 10000"
"Bonus 5000 credited"
"Refund received 1500"
```

### Past Transactions
```
"Add expense 5000 for shopping on 10th"
"Income 3000 from side project on nov 1"
"Paid 800 for medicines on 15 oct"
```

## Integration with Other Features

### Works With Categories
- Auto-detects your existing categories
- Power users can create new categories on-the-fly

### Works With Budgets
- Transactions added via AI count towards budgets
- Budget alerts still trigger

### Works With Calendar
- View AI-added transactions on calendar
- All dates properly formatted

### Works With Reports
- AI transactions included in all reports
- No difference from manual entries

---

**Start using the AI Assistant today and experience the fastest way to add transactions! 🚀**

**Access:** [http://localhost:8000/ai-assistant/chat/](http://localhost:8000/ai-assistant/chat/)

