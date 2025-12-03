from database import Database
from typing import Optional, Dict, List

def create_entry(entry_number: int, entry_date: str, score: Optional[int] = None,
                energy: Optional[int] = None, mood: Optional[int] = None,
                completed_on_time: bool = False, extra_notes: Optional[str] = None) -> int:
    '''Create a new journal entry'''
    with Database() as db:
        return db.create_entry(entry_number, entry_date, score, energy, mood, completed_on_time, extra_notes)

def get_entry(entry_id: int) -> Optional[Dict]:
    '''Get entry by ID'''
    with Database() as db:
        return db.get_entry(entry_id)

def get_entry_by_date(entry_date: str) -> Optional[Dict]:
    '''Get entry by date'''
    with Database() as db:
        return db.get_entry_by_date(entry_date)

def get_latest_entry_number() -> int:
    '''Get the highest entry number, or 0 if no entries'''
    with Database() as db:
        return db.get_latest_entry_number()

def list_entries(limit: int = 50, offset: int = 0, start_date: Optional[str] = None,
                end_date: Optional[str] = None) -> List[Dict]:
    '''List entries with optional date filtering'''
    with Database() as db:
        return db.list_entries(limit, offset, start_date, end_date)

def update_entry(entry_id: int, score: Optional[int] = None, energy: Optional[int] = None,
                mood: Optional[int] = None, completed_on_time: Optional[bool] = None,
                extra_notes: Optional[str] = None) -> bool:
    '''Update an existing entry'''
    with Database() as db:
        return db.update_entry(entry_id, score, energy, mood, completed_on_time, extra_notes)

def delete_entry(entry_id: int) -> bool:
    '''Delete an entry'''
    with Database() as db:
        return db.delete_entry(entry_id)