import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
import time

# Initialize database
conn = sqlite3.connect('tasks.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        due_date TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
''')
conn.commit()

# Functions
def refresh_tasks(filter_status=None):
    for widget in task_frame.winfo_children():
        widget.destroy()
    if filter_status and filter_status != "All":
        cursor.execute("SELECT id, description, status, due_date FROM tasks WHERE status = ?", (filter_status,))
    else:
        cursor.execute("SELECT id, description, status, due_date FROM tasks")
    for row in cursor.fetchall():
        task_id, description, status, due_date = row
        frame = ttk.Frame(task_frame)
        frame.pack(fill='x', pady=3)

        desc_label = ttk.Label(frame, text=f"{description} (Due: {due_date})", width=50)
        desc_label.pack(side='left', padx=5)

        status_var = tk.StringVar(value=status)
        status_menu = ttk.Combobox(frame, textvariable=status_var, state='readonly', width=15)
        status_menu['values'] = ('todo', 'in-progress', 'done')
        status_menu.pack(side='left', padx=5)
        status_menu.bind("<<ComboboxSelected>>", lambda e, var=status_var, id=task_id: update_status(var.get(), id))

        del_btn = ttk.Button(frame, text="Delete", command=lambda id=task_id: delete_task(id))
        del_btn.pack(side='right', padx=5)

def add_task():
    desc = task_desc_var.get()
    status = status_var.get()
    due = due_date_var.get()
    if desc and status and due:
        now = datetime.now().isoformat()
        cursor.execute("INSERT INTO tasks (description, status, due_date, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                       (desc, status, due, now, now))
        conn.commit()
        task_desc_entry.delete(0, tk.END)
        status_var.set('')
        due_date_var.set('')
        refresh_tasks()
    else:
        messagebox.showwarning("Input Error", "Please enter task description, status, and due date.")

def update_status(new_status, task_id):
    now = datetime.now().isoformat()
    cursor.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?", (new_status, now, task_id))
    conn.commit()
    refresh_tasks()

def delete_task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    refresh_tasks()

def filter_tasks():
    selected_status = filter_var.get()
    refresh_tasks(selected_status)

def update_clock():
    now = time.strftime("%I:%M:%S %p")
    clock_label.config(text=now)
    root.after(1000, update_clock)

def toggle_theme():
    global current_theme
    if current_theme == 'light':
        style.theme_use('clam')
        root.configure(bg='gray20')
        current_theme = 'dark'
    else:
        style.theme_use('default')
        root.configure(bg='SystemButtonFace')
        current_theme = 'light'

# GUI Setup
root = tk.Tk()
root.title("🧠 Task Manager")
root.geometry("700x600")
root.resizable(False, False)

style = ttk.Style()
current_theme = 'light'

# Clock
clock_label = ttk.Label(root, font=('Helvetica', 12))
clock_label.pack(pady=5)
update_clock()

# Theme Toggle Button
theme_btn = ttk.Button(root, text="Toggle Theme", command=toggle_theme)
theme_btn.pack(pady=5)

# Notebook Tabs
notebook = ttk.Notebook(root)
notebook.pack(pady=10, padx=10, fill='both', expand=True)

# Tabs
tabs = {}
for tab_name in ["Today's Tasks", "Upcoming Tasks", "All Tasks"]:
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=tab_name)
    tabs[tab_name] = frame

# Input Section in "All Tasks" Tab
input_frame = ttk.LabelFrame(tabs["All Tasks"], text="➕ Add New Task")
input_frame.pack(pady=10, padx=10, fill='x')

ttk.Label(input_frame, text="Task Description:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
task_desc_var = tk.StringVar()
task_desc_entry = ttk.Entry(input_frame, textvariable=task_desc_var, width=40)
task_desc_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

ttk.Label(input_frame, text="Status:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
status_var = tk.StringVar()
status_menu = ttk.Combobox(input_frame, textvariable=status_var, state='readonly', width=15)
status_menu['values'] = ('todo', 'in-progress', 'done')
status_menu.grid(row=1, column=1, padx=5, pady=5, sticky='w')

ttk.Label(input_frame, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
due_date_var = tk.StringVar()
due_date_entry = ttk.Entry(input_frame, textvariable=due_date_var, width=20)
due_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

add_btn = ttk.Button(input_frame, text="Add Task", command=add_task)
add_btn.grid(row=3, column=0, columnspan=2, pady=10)

# Filter Section
filter_frame = ttk.LabelFrame(tabs["All Tasks"], text="🔍 Filter by Status")
filter_frame.pack(pady=5, padx=10, fill='x')

filter_var = tk.StringVar(value="All")
filter_menu = ttk.Combobox(filter_frame, textvariable=filter_var, state='readonly', width=20)
filter_menu['values'] = ('All', 'todo', 'in-progress', 'done')
filter_menu.pack(side='left', padx=10, pady=5)
filter_menu.bind("<<ComboboxSelected>>", lambda e: filter_tasks())

# Task List Section
task_list_frame = ttk.LabelFrame(tabs["All Tasks"], text="📋 Tasks")
task_list_frame.pack(pady=10, padx=10, fill='both', expand=True)

canvas = tk.Canvas(task_list_frame)
scrollbar = ttk.Scrollbar(task_list_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
task_frame = scrollable_frame

# Function to populate tasks in different tabs
def populate_tabs():
    for tab in ["Today's Tasks", "Upcoming Tasks"]:
        for widget in tabs[tab].winfo_children():
            widget.destroy()

    today = date.today().isoformat()
    cursor.execute("SELECT description, status, due_date FROM tasks")
    tasks = cursor.fetchall()

    for desc, status, due in tasks:
        target_tab = None
        if due == today:
            target_tab = "Today's Tasks"
        elif due > today:
            target_tab = "Upcoming Tasks"

        if target_tab:
            frame = ttk.Frame(tabs[target_tab])
            frame.pack(fill='x', padx=10, pady=4)
            task_str = f"{desc} (Due: {due}) - [{status.upper()}]"
            ttk.Label(frame, text=task_str).pack(side='left')

# Refresh UI
refresh_tasks()
populate_tabs()

# Re-populate tabs every 30 seconds in case of new entries
def auto_update():
    populate_tabs()
    root.after(30000, auto_update)

auto_update()
root.mainloop()
conn.close()
