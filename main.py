import tkinter as tk
from tkinter import ttk
from db_setup import init_db
from ui import build_ui

def main():
    init_db()
    root = tk.Tk()
    root.title("🧠 Task Manager")
    root.geometry("700x600")
    root.resizable(False, False)
    
    style = ttk.Style()
    current_theme = ['light']  # mutable object to pass by reference

    build_ui(root, style, current_theme)

    root.mainloop()

if __name__ == "__main__":
    main()