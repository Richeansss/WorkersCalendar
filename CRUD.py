import sqlite3


def create_worker(name):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO workers (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()


def read_workers():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM workers')
    workers = cursor.fetchall()
    conn.close()
    return workers


def create_task(worker_id, title, start_time, end_time, status):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (worker_id, title, start_time, end_time, status) VALUES (?, ?, ?, ?, ?)',
                   (worker_id, title, start_time, end_time, status))
    conn.commit()
    conn.close()


def read_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks')
    tasks = cursor.fetchall()
    conn.close()
    return tasks
