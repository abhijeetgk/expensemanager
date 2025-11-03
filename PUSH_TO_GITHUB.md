# Push to GitHub - Step by Step Guide

## 🎯 Goal
Upload this Django Expense Manager to: `https://github.com/abhijeetgk/expensemanager`

## 📋 Prerequisites

### 1. Create Repository on GitHub
1. Go to: **https://github.com/new**
2. Fill in:
   - Repository name: `expensemanager`
   - Description: `Django Expense Manager with Admin Dashboard and Analytics`
   - Public or Private: Your choice
   - **IMPORTANT:** Do NOT check "Initialize with README"
3. Click **"Create repository"**

### 2. Identify Your Personal SSH Key

Run this command to see which GitHub account your SSH key is linked to:
```bash
ssh -T git@github.com
```

**Expected output:**
- ✅ Good: `Hi abhijeetgk! You've successfully authenticated...`
- ❌ Problem: `Hi <company-username>! You've successfully authenticated...`

If you see your company username, continue to the SSH configuration section below.

---

## 🚀 Quick Push (If SSH is already configured for personal account)

Run these commands:

```bash
cd /Users/abhijeetkinjawadekar/playground/django/expenseManager

# 1. Configure Git for this repository (use your personal email)
git config user.name "Abhijeet Kinjawadekar"
git config user.email "YOUR_PERSONAL_EMAIL@gmail.com"  # ← UPDATE THIS

# 2. Initialize Git
git init

# 3. Add all files
git add .

# 4. Create initial commit
git commit -m "Initial commit: Django Expense Manager with Admin Dashboard

Features:
- User authentication with role-based access (Admin, Power User, User)
- Income and Expense tracking with categories
- Beautiful admin dashboard with charts and analytics
- User dashboard with transaction management
- Reports with export to PDF/Excel
- Indian Rupee (₹) currency support
- Modern responsive UI with Bootstrap 5
- REST API with JWT authentication
- Advanced OOP patterns and Python best practices"

# 5. Add remote
git remote add origin git@github.com:abhijeetgk/expensemanager.git

# 6. Rename branch to main
git branch -M main

# 7. Push to GitHub
git push -u origin main
```

---

## 🔧 SSH Configuration (If using wrong account)

If `ssh -T git@github.com` shows your company account, you need to configure SSH.

### Option 1: Create SSH Config File

1. Create/edit SSH config:
```bash
nano ~/.ssh/config
```

2. Add this content (adjust the IdentityFile path to your personal key):
```
# Personal GitHub Account
Host github.com-personal
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes

# Company GitHub Account  
Host github.com-company
  HostName github.com
  User git
  IdentityFile ~/.ssh/zsah_ssh_key
  IdentitiesOnly yes
```

3. Save and exit (Ctrl+X, then Y, then Enter)

4. Test the connection:
```bash
ssh -T git@github.com-personal
```

Should see: `Hi abhijeetgk! You've successfully authenticated...`

5. Use the modified remote URL:
```bash
git remote add origin git@github.com-personal:abhijeetgk/expensemanager.git
```

### Option 2: Use GIT_SSH_COMMAND

Specify the SSH key directly when pushing:

```bash
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa -o IdentitiesOnly=yes" git push -u origin main
```

---

## ✅ Verification

After pushing, verify:

1. **Check GitHub:**
   - Go to: https://github.com/abhijeetgk/expensemanager
   - You should see all your files

2. **Check Git config:**
```bash
git config user.name
git config user.email
git remote -v
```

3. **Check commit author:**
```bash
git log --oneline -1
```

---

## 🆘 Troubleshooting

### Error: "Permission denied (publickey)"

**Cause:** Wrong SSH key or key not added to GitHub

**Solution:**
1. Check which key is being used:
```bash
ssh -vT git@github.com 2>&1 | grep "identity file"
```

2. Add your personal SSH key to GitHub:
   - Copy your public key: `cat ~/.ssh/id_rsa.pub`
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste and save

### Error: "Repository not found"

**Cause:** Repository doesn't exist on GitHub

**Solution:** Create it first at https://github.com/new

### Error: "fatal: remote origin already exists"

**Solution:**
```bash
git remote remove origin
git remote add origin git@github.com:abhijeetgk/expensemanager.git
```

### Wrong account is committing

**Cause:** Global Git config has company email

**Solution:** Set local config (per repository):
```bash
git config user.email "your-personal@email.com"
git config user.name "Abhijeet Kinjawadekar"
```

---

## 📝 What Gets Pushed

The following will be uploaded:
- ✅ All Python source code
- ✅ Django apps (accounts, categories, transactions, reports, dashboard)
- ✅ Templates (user and admin dashboards)
- ✅ Configuration files
- ✅ Requirements.txt
- ✅ Documentation (README, guides)
- ❌ Virtual environment (excluded by .gitignore)
- ❌ Database file (excluded by .gitignore)
- ❌ .env files (excluded by .gitignore)
- ❌ __pycache__ (excluded by .gitignore)

---

## 🎉 Success!

Once pushed successfully, you can:
1. View your code at: https://github.com/abhijeetgk/expensemanager
2. Share the repository
3. Clone it on other machines
4. Collaborate with others
5. Set up CI/CD pipelines

---

## 📞 Need Help?

If you encounter issues:
1. Check the error message carefully
2. Review the SSH_CONFIG_GUIDE.md file
3. Test SSH connection: `ssh -T git@github.com`
4. Verify repository exists on GitHub
5. Check Git configuration: `git config --list`

