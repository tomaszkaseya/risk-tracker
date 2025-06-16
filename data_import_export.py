#!/usr/bin/env python3
"""
Data Import/Export tool for Risk Tracker
Import epics and risks from CSV files or export to CSV
"""

import csv
import requests
import json
from datetime import datetime, date
import os

BASE_URL = "http://localhost:8000/api"

def export_to_csv():
    """Export all epics and risks to CSV files"""
    print("📤 Exporting data to CSV files...")
    
    try:
        # Export Epics
        response = requests.get(f"{BASE_URL}/epics")
        if response.status_code == 200:
            epics = response.json()
            
            # Create epics CSV
            with open('epics_export.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'title', 'description', 'target_launch_date', 'actual_launch_date', 'status', 'created_at', 'updated_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for epic in epics:
                    # Clean up the data for CSV
                    epic_data = {
                        'id': epic['id'],
                        'title': epic['title'],
                        'description': epic.get('description', ''),
                        'target_launch_date': epic.get('target_launch_date', ''),
                        'actual_launch_date': epic.get('actual_launch_date', ''),
                        'status': epic['status'],
                        'created_at': epic['created_at'],
                        'updated_at': epic['updated_at']
                    }
                    writer.writerow(epic_data)
            
            print(f"✅ Exported {len(epics)} epics to epics_export.csv")
            
            # Export Risks
            all_risks = []
            for epic in epics:
                for risk in epic.get('risks', []):
                    risk_data = {
                        'id': risk['id'],
                        'epic_id': risk['epic_id'],
                        'epic_title': epic['title'],
                        'description': risk['description'],
                        'mitigation_plan': risk.get('mitigation_plan', ''),
                        'date_added': risk['date_added'],
                        'status': risk['status'],
                        'created_at': risk['created_at'],
                        'updated_at': risk['updated_at']
                    }
                    all_risks.append(risk_data)
            
            with open('risks_export.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'epic_id', 'epic_title', 'description', 'mitigation_plan', 'date_added', 'status', 'created_at', 'updated_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_risks)
            
            print(f"✅ Exported {len(all_risks)} risks to risks_export.csv")
            
        else:
            print(f"❌ Failed to fetch epics: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during export: {e}")

def import_from_csv():
    """Import epics from CSV file"""
    print("📥 Importing data from CSV files...")
    
    # Import Epics
    if os.path.exists('epics_import.csv'):
        try:
            with open('epics_import.csv', 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                imported_epics = 0
                
                for row in reader:
                    epic_data = {
                        'title': row['title'],
                        'description': row.get('description', '') or None,
                        'target_launch_date': row.get('target_launch_date', '') or None,
                        'actual_launch_date': row.get('actual_launch_date', '') or None,
                        'status': row.get('status', 'Planned')
                    }
                    
                    response = requests.post(f"{BASE_URL}/epics", json=epic_data)
                    if response.status_code == 200:
                        imported_epics += 1
                        epic = response.json()
                        print(f"✅ Imported epic: {epic['title']} (ID: {epic['id']})")
                    else:
                        print(f"❌ Failed to import epic: {row['title']} - {response.text}")
                
                print(f"📊 Imported {imported_epics} epics from epics_import.csv")
                
        except Exception as e:
            print(f"❌ Error importing epics: {e}")
    else:
        print("📄 No epics_import.csv file found")
    
    # Import Risks (requires epics to exist first)
    if os.path.exists('risks_import.csv'):
        try:
            with open('risks_import.csv', 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                imported_risks = 0
                
                for row in reader:
                    # Find epic by title (since IDs might be different)
                    epic_title = row.get('epic_title', '')
                    if not epic_title:
                        print(f"⚠️  Skipping risk without epic_title: {row.get('description', '')[:50]}...")
                        continue
                    
                    # Get all epics to find the right one
                    epics_response = requests.get(f"{BASE_URL}/epics")
                    if epics_response.status_code != 200:
                        print("❌ Failed to fetch epics for risk import")
                        break
                    
                    epics = epics_response.json()
                    target_epic = None
                    for epic in epics:
                        if epic['title'] == epic_title:
                            target_epic = epic
                            break
                    
                    if not target_epic:
                        print(f"⚠️  Epic not found for risk: {epic_title}")
                        continue
                    
                    risk_data = {
                        'description': row['description'],
                        'mitigation_plan': row.get('mitigation_plan', '') or None,
                        'status': row.get('status', 'Open')
                    }
                    
                    response = requests.post(f"{BASE_URL}/epics/{target_epic['id']}/risks", json=risk_data)
                    if response.status_code == 200:
                        imported_risks += 1
                        print(f"✅ Imported risk for '{epic_title}': {risk_data['description'][:50]}...")
                    else:
                        print(f"❌ Failed to import risk: {response.text}")
                
                print(f"📊 Imported {imported_risks} risks from risks_import.csv")
                
        except Exception as e:
            print(f"❌ Error importing risks: {e}")
    else:
        print("📄 No risks_import.csv file found")

def create_import_templates():
    """Create template CSV files for import"""
    print("📝 Creating import template files...")
    
    # Create epics template
    with open('epics_import_template.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'description', 'target_launch_date', 'actual_launch_date', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Add sample rows
        sample_epics = [
            {
                'title': 'Sample Epic 1',
                'description': 'This is a sample epic description',
                'target_launch_date': '2024-03-15',
                'actual_launch_date': '',
                'status': 'In Progress'
            },
            {
                'title': 'Sample Epic 2',
                'description': 'Another sample epic',
                'target_launch_date': '2024-04-01',
                'actual_launch_date': '',
                'status': 'Planned'
            }
        ]
        writer.writerows(sample_epics)
    
    # Create risks template
    with open('risks_import_template.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['epic_title', 'description', 'mitigation_plan', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Add sample rows
        sample_risks = [
            {
                'epic_title': 'Sample Epic 1',
                'description': 'Sample risk description',
                'mitigation_plan': 'Sample mitigation plan',
                'status': 'Open'
            },
            {
                'epic_title': 'Sample Epic 1',
                'description': 'Another sample risk',
                'mitigation_plan': 'Another mitigation plan',
                'status': 'Mitigating'
            }
        ]
        writer.writerows(sample_risks)
    
    print("✅ Created template files:")
    print("   📄 epics_import_template.csv")
    print("   📄 risks_import_template.csv")
    print("\n💡 Edit these files with your data, then rename them to:")
    print("   📄 epics_import.csv")
    print("   📄 risks_import.csv")
    print("   Then run: python data_import_export.py import")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        print("🚀 Risk Tracker Data Import/Export Tool")
        print("=" * 45)
        print("Usage:")
        print("  python data_import_export.py export     # Export to CSV")
        print("  python data_import_export.py import     # Import from CSV")
        print("  python data_import_export.py template   # Create import templates")
        print()
        print("Files used:")
        print("  📤 Export: epics_export.csv, risks_export.csv")
        print("  📥 Import: epics_import.csv, risks_import.csv")
        
    elif sys.argv[1] == "export":
        export_to_csv()
        
    elif sys.argv[1] == "import":
        import_from_csv()
        
    elif sys.argv[1] == "template":
        create_import_templates()
        
    else:
        print("❌ Invalid command. Use: export, import, or template") 