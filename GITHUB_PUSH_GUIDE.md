# Quick Guide: Push to Personal GitHub

## Overview
- **Your Global Git Config**: Company account (unchanged)
- **This Project Only**: Personal account (abhijeetgk)

## Option 1: Automated Script (Recommended)

Run the setup script:

```bash
./setup_github.sh
```

This will:
1. Set local Git config for this project only (won't touch global)
2. Initialize Git repository
3. Add all files
4. Create initial commit
5. Add remote
6. Push to GitHub

## Option 2: Manual Steps

### Step 1: Create Repository on GitHub
1. Go to: https://github.com/new
2. Repository name: `expensemanager`
3. Don't initialize with README
4. Click "Create repository"

### Step 2: Configure Git (Local Only)
```bash
# Set config for THIS project only (doesn't affect global)
git config user.email "your-personal-email@gmail.com"
```

### Step 3: Initialize and Push
```bash
# Initialize Git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Django Expense Manager with Admin Dashboard"

# Add remote
git remote add origin git@github.com:abhijeetgk/expensemanager.git

# Push
git branch -M main
git push -u origin main
```

## Verify Configuration

Check what email will be used for commits in this project:
```bash
git config user.email  # Shows local (personal) email
```

Check global config (should still be company):
```bash
git config --global user.email  # Shows company email
```

## SSH Key Setup (If Needed)

If you have multiple SSH keys and need to specify which one to use:

### Option A: Create SSH Config
Edit `~/.ssh/config`:
```
Host github.com-personal
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_rsa
  IdentitiesOnly yes
```

Then use:
```bash
git remote set-url origin git@github.com-personal:abhijeetgk/expensemanager.git
```

### Option B: Use GIT_SSH_COMMAND
```bash
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa" git push -u origin main
```

## Test SSH Connection
```bash
ssh -T git@github.com
# Should see: "Hi abhijeetgk! You've successfully authenticated..."
```

## Summary

✅ **Global Config**: Stays as company account (for all other projects)  
✅ **This Project**: Uses personal account (abhijeetgk)  
✅ **No Conflicts**: Local config overrides global for this project only

