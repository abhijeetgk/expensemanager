"""
Natural Language Processing parser for transaction input.

Parses natural language text to extract transaction details.
"""

import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional, List
from dateutil import parser as date_parser


class TransactionParser:
    """Parse natural language transaction input."""
    
    # Keywords for transaction types
    INCOME_KEYWORDS = ['income', 'received', 'got', 'earned', 'salary', 'payment', 'credit']
    EXPENSE_KEYWORDS = ['expense', 'spent', 'paid', 'bought', 'purchase', 'debit', 'cost']
    
    # Common date patterns
    DATE_PATTERNS = {
        'today': lambda: datetime.now().date(),
        'yesterday': lambda: (datetime.now() - timedelta(days=1)).date(),
        'tomorrow': lambda: (datetime.now() + timedelta(days=1)).date(),
    }
    
    def __init__(self):
        """Initialize parser."""
        self.extracted_data = {}
        self.missing_fields = []
        self.confidence = 0.0
    
    def parse(self, text: str) -> Dict:
        """
        Parse natural language text to extract transaction details.
        
        Args:
            text: Natural language input
        
        Returns:
            Dictionary with extracted transaction details
        """
        text = text.lower().strip()
        self.extracted_data = {}
        self.missing_fields = []
        
        # Extract transaction type
        transaction_type = self._extract_type(text)
        if transaction_type:
            self.extracted_data['type'] = transaction_type
        else:
            self.missing_fields.append('type')
        
        # Extract amount
        amount = self._extract_amount(text)
        if amount:
            self.extracted_data['amount'] = amount
        else:
            self.missing_fields.append('amount')
        
        # Extract date
        date = self._extract_date(text)
        if date:
            self.extracted_data['date'] = date
        else:
            self.extracted_data['date'] = datetime.now().date()  # Default to today
        
        # Extract category
        category = self._extract_category(text)
        if category:
            self.extracted_data['category'] = category
        else:
            self.missing_fields.append('category')
        
        # Extract description
        description = self._extract_description(text)
        self.extracted_data['description'] = description
        
        # Extract payment method (for expenses)
        payment_method = self._extract_payment_method(text)
        if payment_method:
            self.extracted_data['payment_method'] = payment_method
        
        # Extract source (for income)
        source = self._extract_source(text)
        if source:
            self.extracted_data['source'] = source
        
        # Calculate confidence
        self.confidence = self._calculate_confidence()
        self.extracted_data['confidence'] = self.confidence
        self.extracted_data['missing_fields'] = self.missing_fields
        
        return self.extracted_data
    
    def _extract_type(self, text: str) -> Optional[str]:
        """Extract transaction type (income or expense)."""
        # Check for income keywords
        for keyword in self.INCOME_KEYWORDS:
            if keyword in text:
                return 'income'
        
        # Check for expense keywords
        for keyword in self.EXPENSE_KEYWORDS:
            if keyword in text:
                return 'expense'
        
        return None
    
    def _extract_amount(self, text: str) -> Optional[Decimal]:
        """Extract amount from text."""
        # Pattern for amounts: rs 1000, ₹1000, 1000 rupees, $1000, 1000.50
        patterns = [
            r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'inr\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:rupees|rs|inr)',
            r'\$\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'(?:of|amount|for)\s+(?:rs\.?\s*)?(\d+(?:,\d+)*(?:\.\d{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return Decimal(amount_str)
                except:
                    pass
        
        return None
    
    def _extract_date(self, text: str) -> Optional[datetime.date]:
        """Extract date from text."""
        # Check for relative dates
        for keyword, date_func in self.DATE_PATTERNS.items():
            if keyword in text:
                return date_func()
        
        # Try to parse explicit dates
        date_patterns = [
            # Format: 03 nov 25, 03 nov 2025, 3 november 2025
            r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{2,4})',
            # Format: nov 03 25, november 3 2025
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})\s+(\d{2,4})',
            # Format: 2025-11-03, 03-11-2025
            r'(\d{2,4})[-/](\d{1,2})[-/](\d{1,2})',
            # Format: on the 15th
            r'on\s+(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(0)
                    parsed_date = date_parser.parse(date_str, fuzzy=True)
                    return parsed_date.date()
                except:
                    pass
        
        return None
    
    def _extract_category(self, text: str) -> Optional[str]:
        """Extract category from text."""
        # Common category keywords
        categories = {
            'salary': ['salary', 'wage', 'paycheck'],
            'freelance': ['freelance', 'contract', 'consulting'],
            'food': ['food', 'groceries', 'restaurant', 'lunch', 'dinner', 'breakfast'],
            'transport': ['transport', 'fuel', 'gas', 'uber', 'taxi', 'travel'],
            'utilities': ['utilities', 'electricity', 'water', 'internet', 'phone', 'mobile'],
            'rent': ['rent', 'lease', 'housing'],
            'entertainment': ['entertainment', 'movie', 'netflix', 'spotify', 'gaming'],
            'shopping': ['shopping', 'clothes', 'clothing', 'fashion'],
            'healthcare': ['healthcare', 'medical', 'doctor', 'medicine', 'hospital'],
            'education': ['education', 'course', 'training', 'tuition', 'books'],
            'savings': ['saving', 'savings', 'investment', 'fixed deposit', 'fd'],
            'transfer': ['transfer', 'transferred', 'wire'],
        }
        
        # Look for category keywords
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        # Look for "under <category>", "for <category>", or "to <category>" pattern
        under_pattern = r'(?:under|for|category|as|to)\s+([a-z\s]+?)(?:\s+(?:on|today|yesterday|tomorrow|\d)|$)'
        match = re.search(under_pattern, text, re.IGNORECASE)
        if match:
            category_text = match.group(1).strip()
            # Return first word if multiple words (e.g., "saving account" -> "saving")
            return category_text.split()[0] if category_text else None
        
        return None
    
    def _extract_description(self, text: str) -> str:
        """Extract description from text."""
        # Remove amount, date, and category references to get description
        cleaned = text
        
        # Remove common phrases
        remove_patterns = [
            r'add\s+(?:income|expense)',
            r'of\s+rs\.?\s*\d+',
            r'under\s+\w+',
            r'on\s+\d{1,2}\s+\w+\s+\d{2,4}',
            r'(?:today|yesterday|tomorrow)',
        ]
        
        for pattern in remove_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up and return
        cleaned = cleaned.strip()
        return cleaned if cleaned else text[:50]  # Fallback to first 50 chars
    
    def _extract_payment_method(self, text: str) -> Optional[str]:
        """Extract payment method for expenses."""
        payment_methods = {
            'CASH': ['cash', 'money'],
            'CREDIT_CARD': ['credit card', 'card', 'cc'],
            'DEBIT_CARD': ['debit card', 'debit'],
            'BANK_TRANSFER': ['bank transfer', 'transfer', 'upi', 'neft', 'imps'],
            'MOBILE_PAYMENT': ['paytm', 'gpay', 'phonepe', 'mobile payment'],
        }
        
        for method, keywords in payment_methods.items():
            for keyword in keywords:
                if keyword in text:
                    return method
        
        return None
    
    def _extract_source(self, text: str) -> Optional[str]:
        """Extract source for income."""
        # Look for "from <source>" pattern
        from_pattern = r'from\s+([a-z\s]+?)(?:\s+on|\s+under|$)'
        match = re.search(from_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score based on extracted fields."""
        total_fields = 4  # type, amount, date, category
        extracted_fields = total_fields - len(self.missing_fields)
        return (extracted_fields / total_fields) * 100


class ConversationalBot:
    """Conversational bot for transaction entry."""
    
    def __init__(self):
        """Initialize bot."""
        self.context = {}
        self.state = 'initial'
        self.parser = TransactionParser()
    
    def process_message(self, message: str, context: Dict = None) -> Dict:
        """
        Process user message and return response.
        
        Args:
            message: User input message
            context: Current conversation context
        
        Returns:
            Dictionary with response and updated context
        """
        if context:
            self.context = context
        
        # Parse the message
        parsed = self.parser.parse(message)
        
        # Update context with parsed data
        self.context.update(parsed)
        
        # Generate response based on what's missing
        response = self._generate_response(parsed)
        
        return {
            'response': response,
            'context': self.context,
            'parsed_data': parsed,
            'ready_to_save': len(parsed['missing_fields']) == 0,
            'confidence': parsed['confidence']
        }
    
    def _generate_response(self, parsed: Dict) -> Dict:
        """Generate appropriate response based on parsed data."""
        missing = parsed.get('missing_fields', [])
        
        if not missing:
            # All required fields extracted
            return {
                'type': 'confirmation',
                'message': self._format_confirmation(parsed),
                'buttons': ['Confirm', 'Edit', 'Cancel']
            }
        
        # Ask for missing information - but only ask once per field
        if 'type' in missing and 'type' not in self.context:
            return {
                'type': 'question',
                'message': "Is this an income or expense?",
                'buttons': ['Income', 'Expense'],
                'field': 'type'
            }
        
        if 'amount' in missing and 'amount' not in self.context:
            return {
                'type': 'question',
                'message': "How much is the amount?",
                'field': 'amount',
                'placeholder': 'e.g., 5000'
            }
        
        if 'category' in missing and 'category' not in self.context:
            return {
                'type': 'question',
                'message': f"What category for this {parsed.get('type', 'transaction')}? (e.g., food, transport, salary, etc.)",
                'field': 'category',
                'requires_fetch': True  # Need to fetch categories from DB
            }
        
        # If we still have missing fields but already asked, show what we have
        if missing:
            # Try to proceed with what we have or ask user to provide complete info
            return {
                'type': 'error',
                'message': f"I'm having trouble understanding. Please provide all details like: 'Add income of ₹10000 under salary today' or 'Spent ₹500 on food yesterday'",
                'buttons': []
            }
        
        return {
            'type': 'confirmation',
            'message': self._format_confirmation(parsed),
            'buttons': ['Confirm', 'Edit', 'Cancel']
        }
    
    def _format_confirmation(self, parsed: Dict) -> str:
        """Format confirmation message."""
        trans_type = parsed.get('type', 'transaction')
        amount = parsed.get('amount', 0)
        category = parsed.get('category', 'unknown')
        date = parsed.get('date', datetime.now().date())
        
        message = f"I'll add this {trans_type}:\n\n"
        message += f"💰 Amount: ₹{amount:,.2f}\n"
        message += f"📁 Category: {category.title()}\n"
        message += f"📅 Date: {date.strftime('%B %d, %Y')}\n"
        
        if parsed.get('description'):
            message += f"📝 Note: {parsed['description']}\n"
        
        if parsed.get('payment_method'):
            message += f"💳 Payment: {parsed['payment_method']}\n"
        
        if parsed.get('source'):
            message += f"🏢 Source: {parsed['source']}\n"
        
        return message

