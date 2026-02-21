import sqlite3
from datetime import date

DB_NAME = 'tracker.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

# === PROJECT MANAGER ===
class Project:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def save(self):
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO projects (name, description) VALUES (?, ?)", 
                      (self.name, self.description))
            conn.commit()

    @staticmethod
    def get_all():
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM projects ORDER BY created_at DESC")
            return c.fetchall()

    @staticmethod
    def delete(project_id):
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            c.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
            conn.commit()

# === TASK MANAGER ===
class Task:
    # ADDED: description=None in init
    def __init__(self, project_id, name, description=None, status='Pending', priority='Medium', due_date=None):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.status = status
        self.priority = priority
        self.due_date = due_date

    def save(self):
        with get_connection() as conn:
            c = conn.cursor()
            # ADDED: description in INSERT
            c.execute("""
                INSERT INTO tasks (project_id, name, description, status, priority, due_date) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.project_id, self.name, self.description, self.status, self.priority, self.due_date))
            conn.commit()

    @staticmethod
    def get_by_project(project_id):
        with get_connection() as conn:
            c = conn.cursor()
            # ADDED: description in SELECT
            c.execute("""
                SELECT id, name, description, status, priority, due_date 
                FROM tasks WHERE project_id = ? 
                ORDER BY status DESC, due_date ASC
            """, (project_id,))
            return c.fetchall()

    @staticmethod
    def update_status(task_id, new_status):
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
            conn.commit()

    # ADDED: new_desc argument
    @staticmethod
    def update_details(task_id, new_name, new_desc, new_priority, new_due_date):
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE tasks 
                SET name = ?, description = ?, priority = ?, due_date = ? 
                WHERE id = ?
            """, (new_name, new_desc, new_priority, new_due_date, task_id))
            conn.commit()

    @staticmethod
    def delete(task_id):
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()