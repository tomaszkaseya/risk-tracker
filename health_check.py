#!/usr/bin/env python3
"""
Risk Tracker System Health Check
Verifies all components are working correctly
"""

import requests
import os
import sqlite3
from datetime import datetime
import sys

def check_server_status():
    """Check if the FastAPI server is running"""
    print("🌐 Checking server status...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding")
            return True
        else:
            print(f"⚠️  Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        print("💡 Start the server with: python run.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def check_api_endpoints():
    """Test critical API endpoints"""
    print("\n🔌 Checking API endpoints...")
    
    endpoints = [
        ("GET", "/api/epics", "List epics"),
        ("GET", "/docs", "API documentation"),
        ("GET", "/openapi.json", "OpenAPI spec")
    ]
    
    all_good = True
    
    for method, endpoint, description in endpoints:
        try:
            url = f"http://localhost:8000{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {description}: {endpoint}")
            else:
                print(f"⚠️  {description}: {endpoint} (Status: {response.status_code})")
                all_good = False
                
        except Exception as e:
            print(f"❌ {description}: {endpoint} - Error: {e}")
            all_good = False
    
    return all_good

def check_database():
    """Check database status and content"""
    print("\n🗄️  Checking database...")
    
    db_file = "risk_tracker.db"
    
    if not os.path.exists(db_file):
        print("❌ Database file not found")
        print("💡 Start the application to create the database")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        expected_tables = ['epics', 'risks', 'risk_updates']
        missing_tables = [table for table in expected_tables if table not in table_names]
        
        if missing_tables:
            print(f"⚠️  Missing tables: {missing_tables}")
        else:
            print("✅ All required tables exist")
        
        # Check record counts
        cursor.execute("SELECT COUNT(*) FROM epics")
        epic_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM risks")
        risk_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM risk_updates")
        update_count = cursor.fetchone()[0]
        
        print(f"📊 Data summary:")
        print(f"   Epics: {epic_count}")
        print(f"   Risks: {risk_count}")
        print(f"   Updates: {update_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'jinja2',
        'aiofiles',
        'aiosmtplib',
        'python-dotenv',
        'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_file_structure():
    """Check if all required files are present"""
    print("\n📁 Checking file structure...")
    
    required_files = [
        'app/main.py',
        'app/models.py',
        'app/database.py',
        'app/crud.py',
        'app/schemas.py',
        'app/email_service.py',
        'app/static/style.css',
        'app/templates/base.html',
        'app/templates/index.html',
        'app/templates/epic_detail.html',
        'app/templates/epics_list.html',
        'requirements.txt',
        'run.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_environment():
    """Check environment configuration"""
    print("\n⚙️  Checking environment configuration...")
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        print("✅ .env file exists")
        
        # Check for email configuration
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        email_vars = ['SMTP_USERNAME', 'SMTP_PASSWORD', 'MANAGER_EMAIL']
        configured_vars = []
        
        for var in email_vars:
            if var in env_content and f"{var}=" in env_content:
                line = [line for line in env_content.split('\n') if line.startswith(f"{var}=")]
                if line and '=' in line[0] and line[0].split('=')[1].strip():
                    configured_vars.append(var)
                    print(f"✅ {var} configured")
                else:
                    print(f"⚠️  {var} not configured")
            else:
                print(f"⚠️  {var} not found")
        
        if len(configured_vars) == len(email_vars):
            print("✅ Email functionality fully configured")
        else:
            print("⚠️  Email functionality partially configured")
            print("💡 Email date change requests may not work")
        
    else:
        print("⚠️  .env file not found")
        print("💡 Copy config.env.example to .env for email configuration")
    
    return True

def test_create_epic():
    """Test creating an epic via API"""
    print("\n🧪 Testing epic creation...")
    
    test_epic = {
        "title": f"Health Check Test Epic {datetime.now().strftime('%H%M%S')}",
        "description": "This is a test epic created by the health check script",
        "status": "Planned"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/epics", json=test_epic, timeout=5)
        if response.status_code == 200:
            epic = response.json()
            epic_id = epic['id']
            print(f"✅ Successfully created test epic (ID: {epic_id})")
            
            # Clean up - delete the test epic
            delete_response = requests.delete(f"http://localhost:8000/api/epics/{epic_id}", timeout=5)
            if delete_response.status_code == 200:
                print("✅ Successfully cleaned up test epic")
            else:
                print(f"⚠️  Test epic cleanup failed (you may need to delete epic ID {epic_id} manually)")
            
            return True
        else:
            print(f"❌ Failed to create test epic: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing epic creation: {e}")
        return False

def main():
    """Run complete health check"""
    print("🚀 Risk Tracker Health Check")
    print("=" * 40)
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    checks = [
        ("Server Status", check_server_status),
        ("Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("Database", check_database),
        ("API Endpoints", check_api_endpoints),
        ("Environment", check_environment),
        ("Epic Creation", test_create_epic)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{'='*20}")
        result = check_func()
        results.append((check_name, result))
    
    # Summary
    print("\n" + "="*40)
    print("🎯 HEALTH CHECK SUMMARY")
    print("="*40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\n📊 Overall Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All systems operational! Your Risk Tracker is ready to use.")
        print("🌐 Visit: http://localhost:8000")
    else:
        print("⚠️  Some issues detected. Please address the failing checks above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 