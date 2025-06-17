#!/usr/bin/env python3
"""
Database Migration Script: Add Projects Support
Migrates the Risk Tracker database to support Projects and Epic-Project relationships
"""

import sqlite3
import os
from datetime import datetime

def backup_database():
    """Create a backup before migration"""
    db_file = "risk_tracker.db"
    if os.path.exists(db_file):
        backup_file = f"risk_tracker_pre_projects_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = os.path.join("backups", backup_file)
        
        # Create backups directory if it doesn't exist
        if not os.path.exists("backups"):
            os.makedirs("backups")
        
        import shutil
        shutil.copy2(db_file, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    return None

def check_migration_needed():
    """Check if migration is needed"""
    db_file = "risk_tracker.db"
    if not os.path.exists(db_file):
        print("❌ Database file not found. Run the application first to create the database.")
        return False
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Check if projects table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects';")
    projects_exists = cursor.fetchone() is not None
    
    # Check if epics table has project_id column
    cursor.execute("PRAGMA table_info(epics);")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    project_id_exists = 'project_id' in column_names
    jira_epic_key_exists = 'jira_epic_key' in column_names
    
    conn.close()
    
    if projects_exists and project_id_exists and jira_epic_key_exists:
        print("✅ Migration already completed - Projects support is already enabled.")
        return False
    
    return True

def run_migration():
    """Execute the database migration"""
    db_file = "risk_tracker.db"
    
    print("🔄 Starting database migration...")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Step 1: Create Projects table
        print("📋 Creating Projects table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jira_project_key VARCHAR(100) UNIQUE,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Step 2: Add project_id column to epics table
        print("🔗 Adding project_id column to epics table...")
        try:
            cursor.execute("ALTER TABLE epics ADD COLUMN project_id INTEGER REFERENCES projects(id);")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("   ℹ️  project_id column already exists")
            else:
                raise
        
        # Step 3: Add jira_epic_key column to epics table
        print("🔑 Adding jira_epic_key column to epics table...")
        try:
            # Add the column without the UNIQUE constraint first
            cursor.execute("ALTER TABLE epics ADD COLUMN jira_epic_key VARCHAR(100);")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("   ℹ️  jira_epic_key column already exists")
            else:
                raise
        
        # Step 4: Create a default "General" project for existing epics
        print("📁 Creating default 'General' project...")
        cursor.execute("""
            INSERT OR IGNORE INTO projects (name, description)
            VALUES ('General', 'Default project for manually created epics');
        """)
        
        # Step 5: Assign existing epics to the General project
        print("🔄 Assigning existing epics to General project...")
        cursor.execute("""
            UPDATE epics 
            SET project_id = (SELECT id FROM projects WHERE name = 'General')
            WHERE project_id IS NULL;
        """)
        
        # Step 6: Create indexes for better performance
        print("⚡ Creating database indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_epics_project_id ON epics(project_id);")
        # Now, create a UNIQUE index on the new column
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_epics_jira_epic_key ON epics(jira_epic_key) WHERE jira_epic_key IS NOT NULL;")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_jira_key ON projects(jira_project_key);")
        
        # Commit all changes
        conn.commit()
        
        # Step 7: Verify migration
        print("🔍 Verifying migration...")
        
        # Check projects table
        cursor.execute("SELECT COUNT(*) FROM projects;")
        project_count = cursor.fetchone()[0]
        
        # Check epics with project assignment
        cursor.execute("SELECT COUNT(*) FROM epics WHERE project_id IS NOT NULL;")
        assigned_epics = cursor.fetchone()[0]
        
        # Check total epics
        cursor.execute("SELECT COUNT(*) FROM epics;")
        total_epics = cursor.fetchone()[0]
        
        print(f"✅ Migration completed successfully!")
        print(f"   📊 Projects: {project_count}")
        print(f"   📊 Assigned Epics: {assigned_epics}/{total_epics}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_migration():
    """Verify the migration was successful"""
    db_file = "risk_tracker.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("\n🔍 Migration Verification:")
    print("=" * 40)
    
    # Check projects table structure
    cursor.execute("PRAGMA table_info(projects);")
    projects_columns = cursor.fetchall()
    print(f"✅ Projects table: {len(projects_columns)} columns")
    
    # Check epics table structure
    cursor.execute("PRAGMA table_info(epics);")
    epics_columns = cursor.fetchall()
    epic_column_names = [col[1] for col in epics_columns]
    
    project_id_exists = 'project_id' in epic_column_names
    jira_epic_key_exists = 'jira_epic_key' in epic_column_names
    
    print(f"✅ Epics table: {len(epics_columns)} columns")
    print(f"   project_id column: {'✅' if project_id_exists else '❌'}")
    print(f"   jira_epic_key column: {'✅' if jira_epic_key_exists else '❌'}")
    
    # Check data
    cursor.execute("SELECT COUNT(*) FROM projects;")
    project_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM epics;")
    epic_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM epics WHERE project_id IS NOT NULL;")
    assigned_count = cursor.fetchone()[0]
    
    print(f"📊 Data summary:")
    print(f"   Projects: {project_count}")
    print(f"   Total Epics: {epic_count}")
    print(f"   Assigned Epics: {assigned_count}")
    
    conn.close()
    
    return project_id_exists and jira_epic_key_exists and assigned_count == epic_count

def main():
    """Main migration function"""
    print("🚀 Risk Tracker Database Migration: Projects Support")
    print("=" * 60)
    
    # Check if migration is needed
    if not check_migration_needed():
        return 0
    
    # Create backup
    backup_path = backup_database()
    if backup_path:
        print(f"💾 Backup created: {backup_path}")
    
    # Confirm with user
    response = input("\n⚠️  This will modify your database. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("🚫 Migration cancelled.")
        return 1
    
    # Run migration
    success = run_migration()
    if not success:
        print("\n❌ Migration failed. Database has been rolled back.")
        return 1
    
    # Verify migration
    if verify_migration():
        print("\n🎉 Migration completed successfully!")
        print("📝 Next steps:")
        print("   1. Restart your Risk Tracker application")
        print("   2. The new Projects features will be available")
        print("   3. Existing epics are assigned to 'General' project")
        return 0
    else:
        print("\n⚠️  Migration completed but verification failed.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 