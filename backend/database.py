import sqlite3
from pathlib import Path
from typing import Optional, Dict, List

DB_PATH = Path(__file__).parent.parent / 'data' / 'jrnscore.db'

class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        '''Runs on start of with statement'''
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Runs on exit of with statement"""
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        
        self.conn.close()
        return False
    
    def _init_db(self):
        '''Initialize the db for the first time with needed tables'''

        # main daily table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_number INTEGER UNIQUE NOT NULL,
                entry_date DATE UNIQUE NOT NULL,
                score INTEGER CHECK(score >= 0 AND score <= 10),
                energy INTEGER CHECK(energy >= 0 AND energy <= 10),
                mood INTEGER CHECK(mood >= 0 AND mood <= 100),
                completed_on_time BOOLEAN DEFAULT 0,
                extra_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
    def create_entry(self, entry_number: int, entry_date: str, 
                     score: Optional[int] = None, energy: Optional[int] = None,
                     mood: Optional[int] = None, completed_on_time: bool = False,
                     extra_notes: Optional[str] = None) -> int:
        '''Add a new jrnscore entry'''

        self.cursor.execute('''
            INSERT INTO entries (entry_number, entry_date, score, energy, 
                                mood, completed_on_time, extra_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entry_number, entry_date, score, energy, mood, completed_on_time, extra_notes))

        return self.cursor.lastrowid
    
    def get_entry_by_date(self, entry_date: str) -> Optional[Dict]:
        '''Retrieve a jrnscore entry from a given date'''
        self.cursor.execute(
            'SELECT * FROM entries WHERE entry_date = ?', 
            (entry_date,)
        )
        row = self.cursor.fetchone()
        return dict(zip(row.keys(), row)) if row else None