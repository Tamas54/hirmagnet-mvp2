# HírMagnet Database Setup Guide

## Database Structure Overview

The HírMagnet application uses SQLite database with the following tables:

### Core Tables

1. **articles** - Main content storage
   - Contains news articles with AI processing metadata
   - Key fields: title, summary, url, source, category, importance_score
   - AI journalist support: assigned_journalist, journalist_name, processing_model

2. **users** - User management with premium features
   - Premium subscription support
   - User preferences and settings

3. **subscriptions** - Stripe subscription management
   - Links to users table
   - Subscription status tracking

4. **social_posts** - Social media content
   - Twitter, Spotify, YouTube integration
   - Associated article tracking

5. **processing_logs** - System operation logs
   - Tracks scraping, AI processing, social posting
   - Performance metrics

6. **site_stats** - Daily statistics
   - Website metrics, AI usage tracking
   - Journalist performance data

7. **ai_journalist_stats** - AI journalist performance
   - Individual journalist metrics
   - Quality and engagement tracking

## Database Configuration

### Location
- **File**: `data/hirmagnet.db`
- **Type**: SQLite database
- **Connection**: `sqlite:///./data/hirmagnet.db`

### Initialization

The database is automatically initialized when needed. The system includes:

1. **Automatic Setup**: Tables are created automatically when the application starts
2. **Migration Support**: Built-in column addition for existing databases
3. **Validation**: Schema validation and health checks

## Database Setup Methods

### Method 1: Automatic Initialization (Recommended)
The database is initialized automatically when you run any main application:

```bash
# Any of these will initialize the database if needed
python hirmagnet_newspaper.py
python test_master.py
python -m api.main
```

### Method 2: Manual Initialization
If you need to manually initialize the database:

```python
from database.db import create_tables
create_tables()
```

### Method 3: Using the Database Checker
Use the provided database checker script:

```bash
python check_database.py
```

This script will:
- Check database file existence
- Verify all tables are present
- Validate table structure
- Show article counts and statistics
- Initialize database if needed

## Database Files Location

```
data/
├── hirmagnet.db              # Main SQLite database
├── daily_premium_counter.txt # Premium usage tracking
├── journalist_daily_usage.json # AI journalist usage stats
└── logs/                     # Application logs
```

## Key Database Functions

### From `database/db.py`:
- `create_tables()` - Initialize all database tables
- `get_db()` - FastAPI dependency for database sessions
- `get_db_session()` - Simple database session for scripts

### From `database/models.py`:
- All SQLAlchemy models and table definitions
- AI journalist configuration
- Validation and helper functions

## Database Schema Highlights

### Articles Table (Core Content)
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    original_title VARCHAR(500),
    summary TEXT,
    original_content TEXT,
    url VARCHAR(1000) UNIQUE NOT NULL,
    source VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    published_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- AI Processing
    is_processed BOOLEAN DEFAULT FALSE,
    ai_summary TEXT,
    ai_title VARCHAR(500),
    sentiment VARCHAR(20),
    importance_score FLOAT DEFAULT 0.0,
    
    -- AI Journalist Support
    assigned_journalist VARCHAR(100),
    journalist_name VARCHAR(200),
    processing_model VARCHAR(50),
    processing_notes TEXT,
    
    -- Media & Engagement
    has_audio BOOLEAN DEFAULT FALSE,
    audio_filename VARCHAR(200),
    view_count INTEGER DEFAULT 0,
    audio_play_count INTEGER DEFAULT 0,
    
    -- Content Flags
    is_breaking BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE
);
```

## Migration and Upgrades

The system includes built-in migration support:

1. **Automatic Column Addition**: New columns are added automatically to existing databases
2. **Backward Compatibility**: Existing data is preserved during updates
3. **Validation Functions**: Built-in validation for data integrity

## Troubleshooting

### Common Issues

1. **Database File Missing**
   - Run `python check_database.py` to initialize
   - Ensure `data/` directory exists

2. **Permission Issues**
   - Check file permissions on `data/` directory
   - Ensure write access for the application

3. **Corrupted Database**
   - Backup existing database
   - Delete `hirmagnet.db` and run initialization

4. **Missing Tables**
   - Run `python check_database.py`
   - Or manually: `from database.db import create_tables; create_tables()`

### Health Check Commands

```bash
# Check database status
python check_database.py

# Verify table structure
python -c "
import sqlite3
conn = sqlite3.connect('data/hirmagnet.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
print([row[0] for row in cursor.fetchall()])
conn.close()
"

# Check article count
python -c "
import sqlite3
conn = sqlite3.connect('data/hirmagnet.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM articles')
print(f'Articles: {cursor.fetchone()[0]}')
conn.close()
"
```

## Best Practices

1. **Regular Backups**: Backup `data/hirmagnet.db` regularly
2. **Monitor Size**: Check database size growth
3. **Clean Old Data**: Implement data retention policies
4. **Index Maintenance**: Monitor query performance
5. **Error Monitoring**: Check application logs for database errors

## Advanced Configuration

### Custom Database URL
Set in `config/settings.py`:
```python
DATABASE_URL = "sqlite:///./data/hirmagnet.db"  # Default
# Or for PostgreSQL:
# DATABASE_URL = "postgresql://user:password@host:port/database"
```

### Connection Pool Settings
For production deployments, consider connection pooling and optimization settings in the engine configuration.