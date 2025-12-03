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

        # analytics table for speed :)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value TEXT,
                date_range TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_metric ON analytics_cache(metric_name, date_range)')

    def _row_to_dict(self, row):
        '''Convert an sqlite row to a dict'''
        return dict(zip(row.keys(), row)) if row else None
        
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
        return self._row_to_dict(row)
    
    def get_entry_by_date(self, entry_date: str) -> Optional[Dict]:
        '''Retrieve a jrnscore entry from a given date'''
        self.cursor.execute('SELECT * FROM entries WHERE entry_date = ?', (entry_date,))
        return self._row_to_dict(self.cursor.fetchone())

    def get_latest_entry_number(self) -> int:
        '''Get the highest entry number, or 0 if no entries'''
        self.cursor.execute('SELECT MAX(entry_number) as max_num FROM entries')
        result = self.cursor.fetchone()
        return result['max_num'] if result['max_num'] else 0

    def list_entries(self, limit: int = 50, offset: int = 0, 
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> List[Dict]:
        '''List entries with optional date filtering'''
        query = 'SELECT * FROM entries WHERE 1=1'
        params = []

        if start_date:
            query += ' AND entry_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND entry_date <= ?'
            params.append(end_date)

        query += ' ORDER BY entry_date DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])

        self.cursor.execute(query, params)
        return [self._row_to_dict(r) for r in self.cursor.fetchall()]

    def update_entry(self, entry_id: int, score: Optional[int] = None, 
                    energy: Optional[int] = None, mood: Optional[int] = None,
                    completed_on_time: Optional[bool] = None,
                    extra_notes: Optional[str] = None) -> bool:
        '''Update an existing entry'''
        updates = []
        params = []

        if score is not None:
            updates.append('score = ?')
            params.append(score)
        if energy is not None:
            updates.append('energy = ?')
            params.append(energy)
        if mood is not None:
            updates.append('mood = ?')
            params.append(mood)
        if completed_on_time is not None:
            updates.append('completed_on_time = ?')
            params.append(completed_on_time)
        if extra_notes is not None:
            updates.append('extra_notes = ?')
            params.append(extra_notes)

        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            query = f"UPDATE entries SET {', '.join(updates)} WHERE id = ?"
            params.append(entry_id)
            self.cursor.execute(query, params)

        return True

    def delete_entry(self, entry_id: int) -> bool:
        '''Delete an entry'''
        self.cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        return True