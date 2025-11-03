#!/bin/bash

# GitHub Setup Script for Personal Account
# This script helps you push to your personal GitHub account when you have multiple SSH keys
# Your global (company) Git config will remain unchanged

echo "═══════════════════════════════════════════════════════"
echo "🚀 GitHub Setup for Personal Account (abhijeetgk)"
echo "═══════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository details
REPO_URL="git@github.com:abhijeetgk/expensemanager.git"

echo "📋 Step 1: Configure Git for THIS project only (local config)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}ℹ${NC}  Your global Git config (company account) will remain unchanged"
echo ""
echo "Current GLOBAL config:"
echo "  Name:  $(git config --global user.name)"
echo "  Email: $(git config --global user.email)"
echo ""
echo "Please enter your PERSONAL GitHub email (for abhijeetgk account):"
read -p "Personal Email: " PERSONAL_EMAIL

# Set local git config (only for this repo, does NOT affect global)
git config user.name "Abhijeet Kinjawadekar"
git config user.email "$PERSONAL_EMAIL"

echo ""
echo -e "${GREEN}✓${NC} Local Git config set for THIS project only:"
echo "  Name:  $(git config user.name)"
echo "  Email: $(git config user.email)"
echo ""
echo -e "${GREEN}✓${NC} Global config unchanged (still your company account)"
echo ""

echo "📋 Step 2: Initialize Git repository"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -d .git ]; then
    git init
    echo -e "${GREEN}✓${NC} Git repository initialized"
else
    echo -e "${YELLOW}!${NC} Git repository already initialized"
fi
echo ""

echo "📋 Step 3: Add remote repository"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if git remote | grep -q "origin"; then
    echo -e "${YELLOW}!${NC} Remote 'origin' already exists. Updating URL..."
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi
echo -e "${GREEN}✓${NC} Remote configured: $REPO_URL"
echo ""

echo "📋 Step 4: Add files to Git"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git add .
echo -e "${GREEN}✓${NC} Files staged for commit"
echo ""

echo "📋 Step 5: Create initial commit"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git commit -m "Initial commit: Django Expense Manager with Admin Dashboard

Features:
- User authentication and role-based access (Admin, Power User, User)
- Income and Expense tracking with categories
- Beautiful admin dashboard with charts and analytics
- User dashboard with transaction management
- Reports with export to PDF/Excel
- Indian Rupee (₹) currency support
- Modern responsive UI with Bootstrap 5
- REST API with JWT authentication
- Advanced OOP patterns and Python best practices"

echo -e "${GREEN}✓${NC} Initial commit created"
echo ""

echo "📋 Step 6: SSH Key Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Available SSH keys:"
ls -la ~/.ssh/*.pub 2>/dev/null | grep -v "total" | awk '{print "  " $9}'
echo ""
echo -e "${YELLOW}IMPORTANT:${NC} You have multiple SSH keys."
echo "Please ensure your personal GitHub SSH key is added to your GitHub account."
echo ""
echo "To check which key is associated with your personal GitHub:"
echo "  1. Go to: https://github.com/settings/keys"
echo "  2. Compare the keys listed there with the keys above"
echo ""
echo "If you need to specify a specific SSH key, create/edit ~/.ssh/config:"
echo ""
echo "Host github.com-personal"
echo "  HostName github.com"
echo "  User git"
echo "  IdentityFile ~/.ssh/id_rsa"
echo "  IdentitiesOnly yes"
echo ""
echo "Then use: git@github.com-personal:abhijeetgk/expensemanager.git"
echo ""

read -p "Press Enter to continue with push, or Ctrl+C to cancel..."

echo ""
echo "📋 Step 7: Push to GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Attempting to push to: $REPO_URL"
echo ""

# Try to push
if git push -u origin main 2>&1 | tee /tmp/git_push.log; then
    echo ""
    echo -e "${GREEN}✓✓✓ SUCCESS! ✓✓✓${NC}"
    echo ""
    echo "Your code has been pushed to GitHub!"
    echo "View it at: https://github.com/abhijeetgk/expensemanager"
else
    echo ""
    echo -e "${RED}✗ Push failed${NC}"
    echo ""
    echo "Common issues and solutions:"
    echo ""
    echo "1. Repository doesn't exist:"
    echo "   Create it at: https://github.com/new"
    echo "   Name: expensemanager"
    echo ""
    echo "2. SSH key not recognized:"
    echo "   Test with: ssh -T git@github.com"
    echo "   Should see: 'Hi abhijeetgk!'"
    echo ""
    echo "3. Wrong SSH key being used:"
    echo "   Create ~/.ssh/config with personal key settings"
    echo ""
    echo "4. Branch name issue:"
    echo "   Try: git branch -M main"
    echo "   Then: git push -u origin main"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Setup Complete!"
echo "═══════════════════════════════════════════════════════"

