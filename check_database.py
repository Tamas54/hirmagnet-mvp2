#!/usr/bin/env python3
"""
Database Status Checker for HírMagnet
=====================================
This script checks the database status and can initialize it if needed.
"""

import os
import sys
import sqlite3
from datetime import datetime

def check_database_status():
    """Check database file and table structure"""
    print("🔍 HírMagnet Database Status Check")
    print("=" * 50)
    
    # Check if database file exists
    db_path = "data/hirmagnet.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    print(f"✅ Database file exists: {db_path}")
    file_size = os.path.getsize(db_path)
    print(f"📊 File size: {file_size:,} bytes")
    
    try:
        # Connect and check tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📋 Found {len(tables)} tables:")
        expected_tables = [
            'users', 'articles', 'social_posts', 'processing_logs', 
            'site_stats', 'ai_journalist_stats', 'subscriptions'
        ]
        
        for table in expected_tables:
            if table in tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} - MISSING!")
        
        # Check articles table structure specifically
        if 'articles' in tables:
            cursor.execute("PRAGMA table_info(articles)")
            columns = cursor.fetchall()
            print(f"\n🗃️ Articles table: {len(columns)} columns")
            
            # Check for important columns
            column_names = [col[1] for col in columns]
            important_columns = [
                'id', 'title', 'summary', 'url', 'source', 'category',
                'importance_score', 'assigned_journalist', 'journalist_name'
            ]
            
            missing_columns = []
            for col in important_columns:
                if col not in column_names:
                    missing_columns.append(col)
            
            if missing_columns:
                print(f"  ⚠️ Missing columns: {', '.join(missing_columns)}")
            else:
                print("  ✅ All important columns present")
            
            # Check record count
            cursor.execute("SELECT COUNT(*) FROM articles")
            article_count = cursor.fetchone()[0]
            print(f"  📊 Total articles: {article_count:,}")
            
            if article_count > 0:
                cursor.execute("SELECT COUNT(*) FROM articles WHERE created_at >= datetime('now', '-24 hours')")
                recent_count = cursor.fetchone()[0]
                print(f"  📊 Recent articles (24h): {recent_count:,}")
        
        conn.close()
        print(f"\n✅ Database check completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def initialize_database():
    """Initialize the database using the create_tables function"""
    print("\n🔧 Initializing database...")
    
    try:
        # Import and run create_tables
        from database.db import create_tables
        create_tables()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main function"""
    print(f"🕐 Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check current status
    status_ok = check_database_status()
    
    if not status_ok:
        print("\n🔧 Database issues detected. Attempting to initialize...")
        if initialize_database():
            print("\n🔄 Re-checking database after initialization...")
            check_database_status()
        else:
            print("❌ Failed to initialize database")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Database is ready for use!")
    print("\n🚀 You can now run:")
    print("  - python hirmagnet_newspaper.py  (main application)")
    print("  - python test_master.py         (test system)")
    print("  - python -m api.main            (API server only)")

if __name__ == "__main__":
    main()