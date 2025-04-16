import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from logic import get_tasks_by_status, add_task, delete_task, update_status
from theme import toggle_theme
from tkcalendar import DateEntry  # For better date selection
from tkinter import filedialog  # For import/export
import json  # For import/export functionality
from logic import suggest_priority
import threading

def generate_date_list():
    base = datetime.today()
    return [(base + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]

def format_date(date_str):
    date_obj = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
    return date_obj.strftime('%d %B %Y')

def build_ui(root, style, current_theme):
    def on_add():
        desc, stat, due = desc_var.get(), stat_var.get(), due_var.get()
        if not desc or not stat or not due:
            messagebox.showwarning("Missing", "Please fill all fields")
            return
        try:
            add_task(desc, stat, due)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add task: {e}")
            return
        refresh()
        clear_form()
        messagebox.showinfo("Success", "Task added successfully!")

    def on_delete(tid):
        try:
            delete_task(tid)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete task: {e}")
            return
        refresh()
        messagebox.showinfo("Success", "Task deleted successfully!")

    def on_status_change(event, tid, var):
        try:
            update_status(tid, var.get())
            refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update task status: {e}")
            return

    def clear_form():
        desc_var.set("")
        stat_var.set("todo")
        due_var.set(date_options[0])

    def toggle_column(frame):
        if frame.winfo_viewable():
            frame.pack_forget()
        else:
            frame.pack(fill='both', expand=True)

    def toggle_fullscreen():
        is_fullscreen = root.attributes('-fullscreen')
        root.attributes('-fullscreen', not is_fullscreen)

    # ========== FORM ==========
    form = ttk.LabelFrame(root, text="Add New Task")
    form.pack(padx=10, pady=10, fill='x')

    desc_var, stat_var, due_var = tk.StringVar(), tk.StringVar(value="todo"), tk.StringVar()
    date_options = generate_date_list()
    due_var.set(date_options[0])

    ttk.Label(form, text="Description").grid(row=0, column=0, padx=5, pady=5, sticky='w')
    ttk.Entry(form, textvariable=desc_var, width=40).grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form, text="Status").grid(row=1, column=0, padx=5, pady=5, sticky='w')
    ttk.Combobox(form, textvariable=stat_var, values=['todo', 'in-progress', 'done'], state='readonly').grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form, text="Due Date").grid(row=2, column=0, padx=5, pady=5, sticky='w')
    ttk.Combobox(form, textvariable=due_var, values=date_options, state='readonly').grid(row=2, column=1, padx=5, pady=5)

    ttk.Button(form, text="Add Task", command=on_add).grid(row=3, column=0, columnspan=2, pady=10)
    ttk.Button(form, text="Full Screen", command=toggle_fullscreen).grid(row=4, column=0, columnspan=2, pady=10)
    ttk.Button(root, text="Toggle Theme", command=lambda: toggle_theme(current_theme, root, style)).pack(pady=5)

    # ========== SCROLLABLE TASK BOARD ==========
    canvas = tk.Canvas(root, height=400)
    h_scroll = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=h_scroll.set)

    canvas.pack(fill='both', expand=True, padx=10)
    h_scroll.pack(fill='x')

    columns_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=columns_frame, anchor='nw')

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    columns_frame.bind("<Configure>", on_frame_configure)

    # Create 3 collapsible columns with Treeview
    def create_column(parent, title):
        col = ttk.Frame(parent)
        header = ttk.Button(col, text=title, command=lambda: toggle_column(content))
        header.pack(fill='x')
        content = ttk.Frame(col)
        content.pack(fill='both', expand=True)
        col.pack(side='left', fill='y', expand=False, padx=10)

        # Create Treeview
        tree = ttk.Treeview(content, columns=("Description", "Status", "Created", "Updated"), show='headings')
        tree.heading("Description", text="Description")
        tree.heading("Status", text="Status")
        tree.heading("Created", text="Created")
        tree.heading("Updated", text="Updated")
        tree.pack(fill='both', expand=True)

        return tree

    todo_tree = create_column(columns_frame, "📋 To-Do")
    progress_tree = create_column(columns_frame, "🔄 In Progress")
    done_tree = create_column(columns_frame, "✅ Done")

    def refresh():
        for tree in [todo_tree, progress_tree, done_tree]:
            tree.delete(*tree.get_children())

        for status, tree in [("todo", todo_tree), ("in-progress", progress_tree), ("done", done_tree)]:
            for tid, desc, stat, updated, created in get_tasks_by_status(status):
                formatted_created = format_date(created)
                formatted_updated = format_date(updated)
                tree.insert("", "end", values=(desc, stat, formatted_created, formatted_updated))

    refresh()
