#  Push to GitHub

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `library_management_system`
3. Description: "Full-stack Library Management System with Django & JavaScript"
4. Choose Public or Private
5. Click "Create repository"

## Step 2: Initialize Git (First Time Only)

### Windows
```cmd
cd c:\Users\acer\library_management_system
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git init
git add .
git commit -m "Initial commit: Library Management System"
```

### Mac/Linux
```bash
cd ~/library_management_system
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git init
git add .
git commit -m "Initial commit: Library Management System"
```

## Step 3: Push to GitHub

```bash
# Add remote repository
git remote add origin https://github.com/yourusername/library_management_system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Update Existing Repository

```bash
git add .
git commit -m "Update: Frontend improvements and database setup"
git push origin main
```

##  What Gets Pushed

 Included:
- library/ (Django app)
- library_config/ (Settings)
- templates/ (Frontend HTML)
- manage.py
- requirements.txt
- README.md
- seed.py
- .gitignore

 Excluded (.gitignore):
- venv/ (Virtual environment)
- *.pyc
- __pycache__/
- *.sqlite3
- media/
- .env
- .vscode/
- .idea/

##  GitHub Links

After pushing, visit:
- Repository: https://github.com/yourusername/library_management_system
- Issues: https://github.com/yourusername/library_management_system/issues
- Settings: https://github.com/yourusername/library_management_system/settings

##  Checklist

- [ ] Created GitHub account (https://github.com)
- [ ] Created new repository on GitHub
- [ ] Configured git user name and email
- [ ] Initialized git repository locally
- [ ] Added all files (git add .)
- [ ] Made initial commit
- [ ] Added GitHub as remote
- [ ] Pushed to GitHub

##  Common Commands

```bash
# Check git status
git status

# View commit history
git log

# Create new branch
git checkout -b feature-branch

# Switch branch
git checkout main

# Merge branch
git merge feature-branch

# Pull latest changes
git pull origin main

# Stash changes
git stash

# View remote URLs
git remote -v
```

##  Important Notes

1. **Never commit .env file** (add to .gitignore)
2. **Never commit venv/** (already in .gitignore)
3. **Never commit sensitive data** (passwords, API keys)
4. **Use meaningful commit messages**
5. **Push regularly** to avoid losing work

##  Troubleshooting

### Git not found
- Download from https://git-scm.com/

### Permission denied
```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096

# Add to GitHub Settings > SSH Keys
```

### Merge conflicts
```bash
# Resolve conflicts manually, then:
git add .
git commit -m "Resolve merge conflicts"
git push origin main
```

### Undo last commit
```bash
git reset --soft HEAD~1
```

---

**Need help?** Visit: https://docs.github.com/
