# 🎯 Command Reference - CropCare AI

Quick reference for all commands needed to set up and run the application.

## Initial Setup Commands

### 1. Navigate to Project Directory
```bash
cd "C:\CropCare AI"
```

### 2. Activate Virtual Environment

**PowerShell:**
```bash
venv\Scripts\Activate.ps1
```

**Command Prompt (CMD):**
```bash
venv\Scripts\activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create AI Model
```bash
python create_model.py
```

### 5. Run Django Development Server
```bash
python manage.py runserver
```

## Access the Application

- **Home Page**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/ (after creating superuser)

## Django Management Commands

### Database Operations
```bash
# Apply migrations
python manage.py migrate

# Create migration files
python manage.py makemigrations

# Create superuser for admin access
python manage.py createsuperuser

# Reset database (WARNING: deletes all data)
python manage.py flush
```

### Server Operations
```bash
# Run development server (default port 8000)
python manage.py runserver

# Run on specific port
python manage.py runserver 8001

# Run on all network interfaces
python manage.py runserver 0.0.0.0:8000
```

### Utility Commands
```bash
# Open Django shell
python manage.py shell

# Check project for common issues
python manage.py check

# Collect static files (for production)
python manage.py collectstatic

# Show installed apps
python manage.py showmigrations
```

## Virtual Environment Management

### Deactivate Virtual Environment
```bash
deactivate
```

### Create New Virtual Environment (if needed)
```bash
python -m venv venv
```

### Upgrade pip
```bash
python -m pip install --upgrade pip
```

## Pip Package Management

### Install Specific Package
```bash
pip install package_name
```

### Uninstall Package
```bash
pip uninstall package_name
```

### List Installed Packages
```bash
pip list
```

### Update requirements.txt
```bash
pip freeze > requirements.txt
```

## Model Operations

### Generate New Model
```bash
python create_model.py
```

### Verify Model File
```bash
# Windows - Check if file exists
if exist "model\plant_model.h5" (echo Model exists) else (echo Model not found)

# PowerShell
Test-Path "model\plant_model.h5"
```

## Testing & Debugging

### Enable Debug Mode
In `Crop/settings.py`, ensure:
```python
DEBUG = True
```

### Run Django Test Suite
```bash
python manage.py test
python manage.py test Crop_Detection
```

### Interactive Shell Session
```bash
python manage.py shell
>>> from Crop_Detection.model_loader import predict_disease
>>> # Test prediction functions
```

## File Operations

### Check Project Structure
```bash
# List project root files
dir

# List Crop_Detection app
dir Crop_Detection

# List templates
dir Crop_Detection\templates

# List model directory
dir model
```

### Clean Up (Optional)

### Delete Cache Files
```bash
# Windows
rmdir /s __pycache__
del *.pyc

# Find and remove all __pycache__ directories
for /d /r . %d in (__pycache__) do @if exist "%d" rmdir /s /q "%d"
```

### Clear Database
```bash
# Remove database file (WARNING: deletes all data)
del db.sqlite3

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

## Production Commands

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Create Superuser for Admin
```bash
python manage.py createsuperuser
```

### Check Deployment Readiness
```bash
python manage.py check --deploy
```

## Troubleshooting Commands

### Check Python Version
```bash
python --version
```

### Check pip Version
```bash
pip --version
```

### Verify TensorFlow Installation
```bash
python -c "import tensorflow; print(tensorflow.__version__)"
```

### Test Django Setup
```bash
python manage.py check
```

### Show All Settings
```bash
python manage.py shell
>>> from django.conf import settings
>>> settings.INSTALLED_APPS
>>> settings.BASE_DIR
```

## Quick Start One-Liner (After First Setup)

Once everything is installed, you can start the server with:

```bash
venv\Scripts\Activate.ps1; python manage.py runserver
```

## Environment Variables (Optional)

Create a `.env` file for sensitive settings:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=your-gemini-api-key-here
# or if your deploy platform uses GOOGLE_API_KEY:
# GOOGLE_API_KEY=your-gemini-api-key-here
```

Load in settings.py:
```python
from decouple import config
DEBUG = config('DEBUG', default=True, cast=bool)
```

## Useful Shortcuts

### Run with Auto-Reload
```bash
python manage.py runserver --reload
```

### Run Tests with Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Format Code (Optional)
```bash
pip install black
black .
```

## Port Troubleshooting

### Find Process Using Port 8000
```bash
# PowerShell
Get-NetTCPConnection -LocalPort 8000

# CMD
netstat -ano | findstr :8000
```

### Kill Process Using Port
```bash
# PowerShell (as Administrator)
Stop-Process -Id <PID> -Force

# CMD (as Administrator)
taskkill /PID <PID> /F
```

---

**Save this file as a quick reference while developing! 📋**
