import sqlite3
from datetime import datetime

def init_db(db_name='vehicle_log.db'):
    """Initializes the database and creates the logs table."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            vehicle_type TEXT,
            license_plate TEXT NOT NULL,
            toll_charge REAL DEFAULT 0.0
        )
    """)
    # Add toll_charge column if it doesn't exist
    cursor.execute("PRAGMA table_info(logs)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'toll_charge' not in columns:
        cursor.execute("ALTER TABLE logs ADD COLUMN toll_charge REAL DEFAULT 0.0")
    conn.commit()
    conn.close()

def log_vehicle(license_plate, vehicle_type='Unknown', toll_charge=0.0, db_name='vehicle_log.db'):
    """Logs a vehicle's data into the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO logs (timestamp, vehicle_type, license_plate, toll_charge)
        VALUES (?, ?, ?, ?)
    """, (timestamp, vehicle_type, license_plate, toll_charge))
    conn.commit()
    conn.close()

def get_all_logs(db_name='vehicle_log.db'):
    """Retrieves all logs from the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, vehicle_type, license_plate, toll_charge FROM logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def clear_logs(db_name='vehicle_log.db'):
    """Clears all logs from the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Example usage:
    init_db()
    log_vehicle('AB1234CD', 'Car', 50.0)
    print(get_all_logs())
    # clear_logs()