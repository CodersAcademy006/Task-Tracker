import sqlite3

DB = 'tasks.db'

def check_schema():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(tasks);")
    schema = cursor.fetchall()
    conn.close()
    return schema

if __name__ == "__main__":
    schema_info = check_schema()
    for column in schema_info:
        print(column)
