import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFormLayout, QLineEdit, QLabel, QTabWidget, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QDate


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Task Manager')
        self.setGeometry(100, 100, 1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.worker_tab = QWidget()
        self.task_tab = QWidget()

        self.tabs.addTab(self.worker_tab, 'Workers')
        self.tabs.addTab(self.task_tab, 'Tasks')

        self.setup_worker_tab()
        self.setup_task_tab()

        # Connect tab change signal to data update method
        self.tabs.currentChanged.connect(self.update_data)

        # Initial data load
        self.update_data()

    def setup_worker_tab(self):
        self.worker_layout = QVBoxLayout()
        self.worker_list = QListWidget()
        self.worker_layout.addWidget(self.worker_list)

        self.worker_form = QFormLayout()
        self.worker_name_input = QLineEdit()
        self.worker_form.addRow(QLabel('Worker Name:'), self.worker_name_input)

        self.worker_buttons_layout = QVBoxLayout()
        self.add_worker_button = QPushButton('Add Worker')
        self.remove_worker_button = QPushButton('Remove Worker')
        self.worker_buttons_layout.addWidget(self.add_worker_button)
        self.worker_buttons_layout.addWidget(self.remove_worker_button)

        self.worker_layout.addLayout(self.worker_form)
        self.worker_layout.addLayout(self.worker_buttons_layout)

        self.worker_tab.setLayout(self.worker_layout)

        # Connect buttons to methods
        self.add_worker_button.clicked.connect(self.add_worker)
        self.remove_worker_button.clicked.connect(self.remove_worker)

    def setup_task_tab(self):
        self.task_layout = QVBoxLayout()
        self.task_table = QTableWidget()
        self.task_layout.addWidget(self.task_table)

        self.task_form = QFormLayout()
        self.task_worker_input = QComboBox()
        self.task_title_input = QLineEdit()
        self.task_start_input = QDateEdit()
        self.task_end_input = QDateEdit()
        self.task_status_input = QComboBox()

        self.initialize_task_form()

        self.task_buttons_layout = QVBoxLayout()
        self.add_task_button = QPushButton('Add Task')
        self.remove_task_button = QPushButton('Remove Task')
        self.task_buttons_layout.addWidget(self.add_task_button)
        self.task_buttons_layout.addWidget(self.remove_task_button)

        self.task_layout.addLayout(self.task_form)
        self.task_layout.addLayout(self.task_buttons_layout)

        self.task_tab.setLayout(self.task_layout)

        # Connect buttons to methods
        self.add_task_button.clicked.connect(self.add_task)
        self.remove_task_button.clicked.connect(self.remove_task)

    def initialize_task_form(self):
        self.task_start_input.setDisplayFormat('dd.MM.yyyy')
        self.task_start_input.setCalendarPopup(True)
        self.task_start_input.setDate(QDate.currentDate())

        self.task_end_input.setDisplayFormat('dd.MM.yyyy')
        self.task_end_input.setCalendarPopup(True)
        self.task_end_input.setDate(QDate.currentDate())

        self.task_status_input.addItems(['In Progress', 'Completed', 'Paused'])

        self.task_form.addRow(QLabel('Worker:'), self.task_worker_input)
        self.task_form.addRow(QLabel('Title:'), self.task_title_input)
        self.task_form.addRow(QLabel('Start Date:'), self.task_start_input)
        self.task_form.addRow(QLabel('End Date:'), self.task_end_input)
        self.task_form.addRow(QLabel('Status:'), self.task_status_input)

    def update_data(self):
        current_index = self.tabs.currentIndex()
        if current_index == 0:  # Workers tab
            self.load_workers()
        elif current_index == 1:  # Tasks tab
            workers = self.load_workers()  # Update worker combo box
            self.task_worker_input.clear()
            self.task_worker_input.addItems([w[1] for w in workers])
            self.load_tasks()

    def add_worker(self):
        name = self.worker_name_input.text().strip()
        if name:
            try:
                with sqlite3.connect('tasks.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO workers (name) VALUES (?)', (name,))
                    conn.commit()
                self.worker_name_input.clear()
                self.update_data()
            except Exception as e:
                print(f"Error adding worker: {e}")
        else:
            print("Worker name is empty.")

    def remove_worker(self):
        selected_items = self.worker_list.selectedItems()
        if selected_items:
            selected_worker = selected_items[0].text()
            try:
                workers = self.load_workers()
                worker_id = next((w[0] for w in workers if w[1] == selected_worker), None)
                if worker_id:
                    with sqlite3.connect('tasks.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM workers WHERE id = ?', (worker_id,))
                        conn.commit()
                    self.update_data()
                else:
                    print(f"No worker found with name: {selected_worker}")
            except Exception as e:
                print(f"Error removing worker: {e}")
        else:
            print("No worker selected.")

    def add_task(self):
        worker_name = self.task_worker_input.currentText()
        title = self.task_title_input.text().strip()
        start_date = self.task_start_input.date().toString('yyyy-MM-dd')
        end_date = self.task_end_input.date().toString('yyyy-MM-dd')
        status = self.task_status_input.currentText()

        workers = self.load_workers()
        worker_id = next((w[0] for w in workers if w[1] == worker_name), None)

        if title and worker_id:
            try:
                with sqlite3.connect('tasks.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO tasks (worker_id, title, start_date, end_date, status) VALUES (?, ?, ?, ?, ?)',
                        (worker_id, title, start_date, end_date, status)
                    )
                    conn.commit()
                self.task_title_input.clear()
                self.task_status_input.setCurrentIndex(0)
                self.update_data()
            except Exception as e:
                print(f"Error adding task: {e}")
        else:
            print("Title or worker ID is empty.")

    def remove_task(self):
        selected_items = self.task_table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            task_id = self.task_table.item(selected_row, 0).text()
            try:
                with sqlite3.connect('tasks.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                    conn.commit()
                self.update_data()
            except Exception as e:
                print(f"Error removing task: {e}")
        else:
            print("No task selected.")

    def load_workers(self):
        try:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM workers')
                workers = cursor.fetchall()
            self.worker_list.clear()
            for worker in workers:
                self.worker_list.addItem(worker[1])
            return workers
        except Exception as e:
            print(f"Error loading workers: {e}")
            return []

    def load_tasks(self):
        try:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT tasks.id, workers.name, tasks.title, tasks.start_date, tasks.end_date, tasks.status
                    FROM tasks
                    JOIN workers ON tasks.worker_id = workers.id
                ''')
                tasks = cursor.fetchall()

            self.task_table.setRowCount(len(tasks))
            self.task_table.setColumnCount(6)
            self.task_table.setHorizontalHeaderLabels(['ID', 'Worker', 'Title', 'Start Date', 'End Date', 'Status'])

            for row, task in enumerate(tasks):
                for column, item in enumerate(task):
                    self.task_table.setItem(row, column, QTableWidgetItem(str(item)))
        except Exception as e:
            print(f"Error loading tasks: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
