"""
Database Migration Script
Drops all existing tables and recreates them with the new schema
WARNING: This will delete all existing data!
"""

from app.db import Base, engine
from app.models import User, Assessment, Question, Result

def migrate():
    print('🔄 Starting database migration...')

    # Drop all tables
    print('📦 Dropping all existing tables...')
    Base.metadata.drop_all(bind=engine)

    # Recreate all tables with new schema
    print('🏗️  Creating all tables with updated schema...')
    Base.metadata.create_all(bind=engine)

    print('✅ Database migration completed successfully!')
    print('\nTables created:')
    print('  - users')
    print('  - assessments')
    print('  - question_bank')
    print('  - exam_results')

if __name__ == '__main__':
    migrate()
