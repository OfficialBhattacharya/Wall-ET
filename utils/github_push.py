import os
import sys
import subprocess
import getpass

def run_command(command, show_output=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True,
            capture_output=True,
            text=True
        )
        if show_output and result.stdout:
            print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        return None

def setup_and_push_repo(repo_name, username=None, token=None, description="Personal Stock Portfolio Tracker and Analyzer"):
    """Set up and push repository to GitHub"""
    # Get current directory (should be StockPicker root)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(root_dir)
    print(f"Working in directory: {root_dir}")
    
    # Check if git is already initialized
    if not os.path.exists(os.path.join(root_dir, '.git')):
        print("Initializing git repository...")
        run_command("git init")
    else:
        print("Git repository already initialized.")
    
    # Create .gitignore if it doesn't exist
    gitignore_path = os.path.join(root_dir, '.gitignore')
    if not os.path.exists(gitignore_path):
        print("Creating .gitignore file...")
        with open(gitignore_path, 'w') as f:
            f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.env
venv/

# VS Code
.vscode/
*.code-workspace

# PyCharm
.idea/

# Personal data files
assets/PersonalFiles/*.csv

# Logs
*.log
logs/

# Jupyter Notebook
.ipynb_checkpoints

# OS specific
.DS_Store
Thumbs.db
""")
    
    # Create README.md if it doesn't exist
    readme_path = os.path.join(root_dir, 'README.md')
    if not os.path.exists(readme_path):
        print("Creating README.md file...")
        with open(readme_path, 'w') as f:
            f.write(f"""# {repo_name}

{description}

## Overview

StockPicker is a personal financial portfolio tracker and analyzer built with Dash and Python. It helps you track your investments across:

- Stocks
- Mutual Funds
- Savings Accounts
- Other Investments

## Features

- Dashboard view of your entire portfolio
- Track stocks, mutual funds and other investments
- Import data from standard Excel holdings statements
- Visualize your investment performance
- Track savings accounts and loans

## Installation

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Run the app: `python app.py`

## Usage

Place your investment data in the appropriate directories:
- `/assets/PersonalFiles/` - Main CSV files for your portfolio
- `/assets/MutualFunds/` - Excel files of mutual fund holdings
- `/assets/Stocks/` - Stock data files

## Utilities

- `utils/mf_excel_converter.py` - Convert mutual fund holdings from Excel to CSV
""")
    
    # Add all files
    print("Adding files to git...")
    run_command("git add .")
    
    # Check if there are any files staged for commit
    status = run_command("git status -s", show_output=False)
    if not status.strip():
        print("No changes to commit. Repository might already be up to date.")
        return
    
    # Make initial commit
    print("Creating initial commit...")
    run_command('git commit -m "Initial commit of StockPicker application"')
    
    # Get GitHub credentials if not provided
    if not username:
        username = input("Enter your GitHub username: ")
    
    # Create remote repo
    repo_url = f"https://github.com/{username}/{repo_name}.git"
    
    # First check if remote origin already exists
    remotes = run_command("git remote -v", show_output=False)
    if "origin" in remotes:
        print("Remote 'origin' already exists. Updating URL...")
        run_command(f"git remote set-url origin {repo_url}")
    else:
        print("Adding remote 'origin'...")
        run_command(f"git remote add origin {repo_url}")
    
    # Push to GitHub
    print(f"Pushing to GitHub repository: {repo_url}")
    
    if token:
        # Use token for authentication
        token_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
        run_command(f"git push -u origin master", show_output=False)
    else:
        # Use credential helper
        print("You'll be prompted for your GitHub password or token...")
        run_command("git push -u origin master")
    
    print(f"\nSuccess! Your code has been pushed to: https://github.com/{username}/{repo_name}")
    print("You can now access your repository in a web browser at the URL above.")

if __name__ == "__main__":
    print("=" * 80)
    print("GitHub Repository Push Utility for StockPicker")
    print("=" * 80)
    
    # Get repository info from command line or prompt
    if len(sys.argv) > 1:
        repo_name = sys.argv[1]
    else:
        repo_name = input("Enter the GitHub repository name to create/use: ")
    
    if len(sys.argv) > 2:
        username = sys.argv[2]
    else:
        username = input("Enter your GitHub username: ")
    
    # Ask if the user wants to use a token
    use_token = input("Do you want to use a GitHub token for authentication? (y/n): ").lower() == 'y'
    token = None
    
    if use_token:
        print("Note: Your token should have 'repo' scope permissions.")
        token = getpass.getpass("Enter your GitHub token: ")
    
    # Run the push process
    setup_and_push_repo(repo_name, username, token) 