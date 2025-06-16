#!/usr/bin/env python3
"""
Database backup script for Risk Tracker
Creates timestamped backups of the SQLite database
"""

import shutil
import os
from datetime import datetime

def backup_database():
    """Create a timestamped backup of the database"""
    
    # Database file location
    db_file = "risk_tracker.db"
    
    if not os.path.exists(db_file):
        print("❌ Database file not found. Make sure the application has been run at least once.")
        return False
    
    # Create backups directory if it doesn't exist
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"📁 Created backups directory: {backup_dir}")
    
    # Generate timestamp for backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"risk_tracker_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Copy the database file
        shutil.copy2(db_file, backup_path)
        
        # Get file size for confirmation
        file_size = os.path.getsize(backup_path)
        file_size_kb = round(file_size / 1024, 2)
        
        print(f"✅ Database backup created successfully!")
        print(f"📄 Backup file: {backup_path}")
        print(f"📊 File size: {file_size_kb} KB")
        print(f"🕒 Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def list_backups():
    """List all existing backups"""
    backup_dir = "backups"
    
    if not os.path.exists(backup_dir):
        print("📁 No backups directory found.")
        return
    
    backups = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
    
    if not backups:
        print("📄 No backup files found.")
        return
    
    print(f"\n📋 Found {len(backups)} backup files:")
    print("-" * 50)
    
    for backup in sorted(backups, reverse=True):
        backup_path = os.path.join(backup_dir, backup)
        file_size = os.path.getsize(backup_path)
        file_size_kb = round(file_size / 1024, 2)
        modified_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
        
        print(f"📄 {backup}")
        print(f"   Size: {file_size_kb} KB")
        print(f"   Date: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def restore_backup(backup_filename):
    """Restore from a backup file"""
    backup_path = os.path.join("backups", backup_filename)
    
    if not os.path.exists(backup_path):
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    # Confirm with user
    response = input(f"⚠️  This will replace the current database. Are you sure? (yes/no): ")
    if response.lower() != 'yes':
        print("🚫 Restore cancelled.")
        return False
    
    try:
        # Backup current database first
        if os.path.exists("risk_tracker.db"):
            current_backup = f"risk_tracker_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2("risk_tracker.db", os.path.join("backups", current_backup))
            print(f"📄 Current database backed up as: {current_backup}")
        
        # Restore from backup
        shutil.copy2(backup_path, "risk_tracker.db")
        print(f"✅ Database restored from: {backup_filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error restoring backup: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        # Default action: create backup
        print("🔄 Creating database backup...")
        backup_database()
        
    elif sys.argv[1] == "list":
        list_backups()
        
    elif sys.argv[1] == "restore" and len(sys.argv) == 3:
        restore_backup(sys.argv[2])
        
    else:
        print("🚀 Risk Tracker Database Backup Tool")
        print("=" * 40)
        print("Usage:")
        print("  python backup_database.py           # Create backup")
        print("  python backup_database.py list      # List all backups")
        print("  python backup_database.py restore <filename>  # Restore from backup")
        print()
        print("Examples:")
        print("  python backup_database.py")
        print("  python backup_database.py list")
        print("  python backup_database.py restore risk_tracker_backup_20241201_143022.db") 