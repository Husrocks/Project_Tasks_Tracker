import sqlite3

def create_tables():
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at DATE DEFAULT CURRENT_DATE
        )
    ''')

    # ADDED: 'description TEXT' column below
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            priority TEXT DEFAULT 'Medium',
            due_date DATE,
            FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("Database ready with Descriptions!")

if __name__ == "__main__":
    create_tables()