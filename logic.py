import sqlite3
from datetime import datetime

DB = 'tasks.db'

def suggest_priority(status, updated_at):
    if status == "done":
        return "Low"

    try:
        # Try full datetime first
        updated_dt = datetime.strptime(updated_at, '%Y-%m-%d %I:%M %p')
    except ValueError:
        try:
            # Try fallback with only time (assume today)
            updated_dt = datetime.strptime(updated_at, '%I:%M %p')
            updated_dt = datetime.combine(datetime.today(), updated_dt.time())
        except Exception:
            return "Unknown"

    hours_passed = (datetime.now() - updated_dt).total_seconds() / 3600

    if hours_passed < 1:
        return "High"
    elif hours_passed < 24:
        return "Medium"
    else:
        return "Low"

def get_tasks_by_status(status):
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE status = ?", (status,))
        tasks = cursor.fetchall()
    except Exception as e:
        raise RuntimeError(f"Error retrieving tasks: {e}")
    finally:
        conn.close()
    return tasks

def add_task(description, status, due_date):
    if not description or not due_date:
        raise ValueError("Description and due date cannot be empty.")
    now = datetime.now().strftime("%I:%M %p")  # store in 12hr format
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (description, status, due_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (description, status, due_date, now, now))
    conn.commit()
    conn.close()

def delete_task(task_id):
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        raise RuntimeError(f"Error deleting task: {e}")

def update_status(task_id, new_status):
    now = datetime.now().strftime("%I:%M %p")
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?", (new_status, now, task_id))
    conn.commit()
    conn.close()
