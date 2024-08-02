import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget, QFormLayout,
                             QLineEdit, QLabel, QTabWidget, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import QDate
import logging

logging.basicConfig(level=logging.INFO)

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

        self.tabs.currentChanged.connect(self.update_data)
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
        self.task_status_input.addItems(['In Progress', 'Completed', 'Paused'])

        self.setup_date_edit(self.task_start_input)
        self.setup_date_edit(self.task_end_input)

        self.task_form.addRow(QLabel('Worker:'), self.task_worker_input)
        self.task_form.addRow(QLabel('Title:'), self.task_title_input)
        self.task_form.addRow(QLabel('Start Date:'), self.task_start_input)
        self.task_form.addRow(QLabel('End Date:'), self.task_end_input)
        self.task_form.addRow(QLabel('Status:'), self.task_status_input)

        self.task_buttons_layout = QVBoxLayout()
        self.add_task_button = QPushButton('Add Task')
        self.remove_task_button = QPushButton('Remove Task')
        self.task_buttons_layout.addWidget(self.add_task_button)
        self.task_buttons_layout.addWidget(self.remove_task_button)

        self.task_layout.addLayout(self.task_form)
        self.task_layout.addLayout(self.task_buttons_layout)

        self.task_tab.setLayout(self.task_layout)

        self.add_task_button.clicked.connect(self.add_task)
        self.remove_task_button.clicked.connect(self.remove_task)

    def setup_date_edit(self, date_edit):
        date_edit.setDisplayFormat('dd.MM.yyyy')
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())

    def update_data(self):
        if self.tabs.currentIndex() == 0:
            self.load_workers()
        elif self.tabs.currentIndex() == 1:
            self.update_task_tab()

    def update_task_tab(self):
        workers = self.load_workers()
        self.task_worker_input.clear()
        self.task_worker_input.addItems([w[1] for w in workers])
        self.load_tasks()

    def add_worker(self):
        name = self.worker_name_input.text()
        if name:
            self.execute_db_command('INSERT INTO workers (name) VALUES (?)', (name,))
            self.worker_name_input.clear()
            self.update_data()
        else:
            logging.warning("Worker name is empty.")

    def remove_worker(self):
        selected_items = self.worker_list.selectedItems()
        if selected_items:
            selected_worker = selected_items[0].text()
            worker_id = [w[0] for w in self.load_workers() if w[1] == selected_worker][0]
            self.execute_db_command('DELETE FROM workers WHERE id = ?', (worker_id,))
            self.update_data()
        else:
            logging.warning("No worker selected.")

    def add_task(self):
        worker_name = self.task_worker_input.currentText()
        title = self.task_title_input.text()
        start_date = self.task_start_input.date().toString('yyyy-MM-dd')
        end_date = self.task_end_input.date().toString('yyyy-MM-dd')
        status = self.task_status_input.currentText()

        workers = self.load_workers()
        worker_id = [w[0] for w in workers if w[1] == worker_name]

        if worker_id and title:
            self.execute_db_command(
                'INSERT INTO tasks (worker_id, title, start_date, end_date, status) VALUES (?, ?, ?, ?, ?)',
                (worker_id[0], title, start_date, end_date, status)
            )
            self.task_title_input.clear()
            self.task_status_input.setCurrentIndex(0)
            self.update_data()
        else:
            logging.warning("Title or worker ID is empty.")

    def remove_task(self):
        selected_items = self.task_table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            task_id = self.task_table.item(selected_row, 0).text()
            self.execute_db_command('DELETE FROM tasks WHERE id = ?', (task_id,))
            self.update_data()
        else:
            logging.warning("No task selected.")

    def load_workers(self):
        return self.execute_db_query('SELECT * FROM workers')

    def load_tasks(self):
        tasks = self.execute_db_query('''
            SELECT tasks.id, workers.name, tasks.title, tasks.start_date, tasks.end_date, tasks.status
            FROM tasks
            JOIN workers ON tasks.worker_id = workers.id
        ''')
        self.task_table.setRowCount(len(tasks))
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels(['ID', 'Worker', 'Title', 'Start Date', 'End Date', 'Status'])

        for row, task in enumerate(tasks):
            for column, item in enumerate(task):
                self.task_table.setItem(row, column, QTableWidgetItem(str(item)))

    def execute_db_command(self, command, params=()):
        try:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                cursor.execute(command, params)
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")

    def execute_db_query(self, query):
        try:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
