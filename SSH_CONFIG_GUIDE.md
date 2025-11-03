# SSH Configuration Guide for Multiple GitHub Accounts

## Problem
You have multiple SSH keys:
- Personal GitHub account (abhijeetgk)
- Company GitHub account

## Solution: Configure SSH to use the correct key

### Step 1: Identify Your Personal SSH Key

Check which SSH key is associated with your personal GitHub account:

```bash
# View your public keys
ls -la ~/.ssh/*.pub

# Display the content of each key
cat ~/.ssh/id_rsa.pub
cat ~/.ssh/vastu.pub
cat ~/.ssh/zsah_ssh_key.pub
```

### Step 2: Verify Key on GitHub

1. Go to: https://github.com/settings/keys
2. Compare the keys listed there with your local keys
3. Identify which key belongs to your personal account (abhijeetgk)

### Step 3: Create/Edit SSH Config

Create or edit `~/.ssh/config`:

```bash
# Edit SSH config
nano ~/.ssh/config
```

Add this configuration (replace `id_rsa` with your personal key name):

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

### Step 4: Update Git Remote URL

For this project (personal account), use:

```bash
# If using the SSH config approach
git remote set-url origin git@github.com-personal:abhijeetgk/expensemanager.git

# OR use the standard URL (if id_rsa is your personal key)
git remote set-url origin git@github.com:abhijeetgk/expensemanager.git
```

### Step 5: Test SSH Connection

```bash
# Test personal account
ssh -T git@github.com-personal
# Should see: "Hi abhijeetgk! You've successfully authenticated..."

# Test company account
ssh -T git@github.com-company
# Should see: "Hi <company-username>! You've successfully authenticated..."
```

## Quick Setup Commands

```bash
# 1. Set local Git config for this repo (not global)
git config user.name "Abhijeet Kinjawadekar"
git config user.email "your-personal-email@gmail.com"  # Use your personal email

# 2. Initialize and add files
git init
git add .

# 3. Create initial commit
git commit -m "Initial commit: Django Expense Manager"

# 4. Add remote (choose one based on your SSH config)
# Option A: With SSH config
git remote add origin git@github.com-personal:abhijeetgk/expensemanager.git

# Option B: Standard (if id_rsa is personal)
git remote add origin git@github.com:abhijeetgk/expensemanager.git

# 5. Push to GitHub
git branch -M main
git push -u origin main
```

## Troubleshooting

### Issue: "Permission denied (publickey)"

**Solution 1:** Check which key is being used
```bash
ssh -vT git@github.com 2>&1 | grep "identity file"
```

**Solution 2:** Force use of specific key
```bash
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa" git push -u origin main
```

### Issue: "Repository not found"

**Solution:** Create the repository first
1. Go to: https://github.com/new
2. Repository name: `expensemanager`
3. Keep it public or private (your choice)
4. Don't initialize with README (we already have files)
5. Click "Create repository"

### Issue: Wrong account being used

**Solution:** Use SSH config with different hosts
```bash
# Update remote to use specific host
git remote set-url origin git@github.com-personal:abhijeetgk/expensemanager.git
```

## Verification

After setup, verify everything:

```bash
# Check Git config
git config user.name
git config user.email

# Check remote
git remote -v

# Test SSH
ssh -T git@github.com
```

## Environment-Specific Git Config

To avoid conflicts, set Git config locally (per repository) instead of globally:

```bash
# Local config (only for this repo)
git config user.email "personal@example.com"

# Global config (all repos)
git config --global user.email "company@example.com"

# Check which is being used
git config user.email  # Shows local if set, otherwise global
```

