#!/usr/bin/env python3
"""
Apply State Board Migration
Creates state_boards table and adds state board columns to syllabus_master
Seeds Telangana and Andhra Pradesh boards
"""

from app.db import Base, engine, SessionLocal
from app.models import StateBoard, StateBoardResource, SyllabusMaster
from sqlalchemy import inspect, text
import sys

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def main():
    print("=" * 80)
    print("STATE BOARD MIGRATION - Telangana & Andhra Pradesh")
    print("=" * 80)

    db = SessionLocal()

    try:
        # Step 1: Create new tables using SQLAlchemy
        print("\n[1/4] Creating state board tables...")
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Tables created (if they didn't exist)")

        # Step 2: Add columns to existing syllabus_master table if they don't exist
        print("\n[2/4] Adding state board columns to syllabus_master...")

        columns_to_add = [
            ('board_type', 'VARCHAR(20)', 'CBSE'),
            ('state_board_id', 'INTEGER', None),
            ('medium', 'VARCHAR(20)', 'English'),
            ('textbook_name', 'VARCHAR(200)', None),
            ('publisher', 'VARCHAR(100)', None),
        ]

        for col_name, col_type, default in columns_to_add:
            if not check_column_exists('syllabus_master', col_name):
                try:
                    default_clause = f" DEFAULT '{default}'" if default else ""
                    alter_sql = f"ALTER TABLE syllabus_master ADD COLUMN {col_name} {col_type}{default_clause};"
                    db.execute(text(alter_sql))
                    db.commit()
                    print(f"  ✅ Added column: {col_name}")
                except Exception as e:
                    db.rollback()
                    print(f"  ⚠️ Could not add {col_name}: {e}")
            else:
                print(f"  ⏭️ Column {col_name} already exists")

        # Step 3: Add foreign key constraint if it doesn't exist
        print("\n[3/4] Adding foreign key constraint...")
        try:
            fk_sql = """
            ALTER TABLE syllabus_master
            ADD CONSTRAINT fk_syllabus_state_board
            FOREIGN KEY (state_board_id) REFERENCES state_boards(id);
            """
            db.execute(text(fk_sql))
            db.commit()
            print("  ✅ Foreign key constraint added")
        except Exception as e:
            db.rollback()
            if 'already exists' in str(e).lower():
                print("  ⏭️ Foreign key constraint already exists")
            else:
                print(f"  ⚠️ Could not add foreign key: {e}")

        # Step 4: Create indexes for better query performance
        print("\n[4/4] Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_syllabus_board_type ON syllabus_master(board_type);",
            "CREATE INDEX IF NOT EXISTS idx_syllabus_state_board ON syllabus_master(state_board_id);",
            "CREATE INDEX IF NOT EXISTS idx_syllabus_medium ON syllabus_master(medium);",
            "CREATE INDEX IF NOT EXISTS idx_resources_board_class ON state_board_resources(state_board_id, class_name);"
        ]

        for idx_sql in indexes:
            try:
                db.execute(text(idx_sql))
                db.commit()
                print(f"  ✅ {idx_sql.split('idx_')[1].split(' ON')[0]}")
            except Exception as e:
                db.rollback()
                print(f"  ⏭️ Index already exists or error: {str(e)[:50]}")

        # Step 5: Seed state boards (Telangana & Andhra Pradesh)
        print("\n[5/5] Seeding state boards...")

        boards_data = [
            {
                'board_code': 'TSBSE',
                'board_name': 'Telangana State Board of Secondary Education',
                'state_name': 'Telangana',
                'website_url': 'https://bse.telangana.gov.in/'
            },
            {
                'board_code': 'BSEAP',
                'board_name': 'Board of Secondary Education, Andhra Pradesh',
                'state_name': 'Andhra Pradesh',
                'website_url': 'https://bse.ap.gov.in/'
            }
        ]

        for board_data in boards_data:
            existing = db.query(StateBoard).filter_by(board_code=board_data['board_code']).first()
            if not existing:
                board = StateBoard(**board_data)
                db.add(board)
                print(f"  ✅ Added: {board_data['board_name']}")
            else:
                print(f"  ⏭️ Already exists: {board_data['board_name']}")

        db.commit()

        # Verification
        print("\n" + "=" * 80)
        print("VERIFICATION")
        print("=" * 80)

        boards = db.query(StateBoard).all()
        print(f"\n✅ State boards in database: {len(boards)}")
        for board in boards:
            print(f"   • {board.board_code}: {board.board_name}")

        # Check syllabus_master columns
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('syllabus_master')]
        state_columns = [col for col in columns if col in ['board_type', 'state_board_id', 'medium', 'textbook_name', 'publisher']]
        print(f"\n✅ State board columns in syllabus_master: {len(state_columns)}/5")
        for col in state_columns:
            print(f"   • {col}")

        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
