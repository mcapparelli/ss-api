#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from infrastructure.psql.db import create_tables

def init_database():
    try:
        create_tables()
        print("✅ Tables created successfully")
        return True
        
    except Exception as e:
        print(e)
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n🎉 Database initialized successfully")
    else:
        print("\n💥 Error initializing database")
        sys.exit(1) 