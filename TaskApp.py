import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget, QFormLayout, \
    QLineEdit, QLabel, QTabWidget, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem, QCalendarWidget
from PyQt5.QtCore import QDate, Qt, QRect
from PyQt5.QtGui import QColor, QPainter, QBrush


def create_tables():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT NOT NULL DEFAULT 'white'  -- Значение по умолчанию
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER,
            title TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (worker_id) REFERENCES workers(id)
        )
    ''')
    conn.commit()
    conn.close()


def update_existing_workers_with_color():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM workers WHERE color IS NULL OR color = ""')
    workers = cursor.fetchall()
    for worker in workers:
        worker_id = worker[0]
        # Установите цвет по умолчанию, например, 'white'
        cursor.execute('UPDATE workers SET color = ? WHERE id = ?', ('white', worker_id))
    conn.commit()
    conn.close()


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
        self.calendar_tab = QWidget()

        self.tabs.addTab(self.worker_tab, 'Workers')
        self.tabs.addTab(self.task_tab, 'Tasks')
        self.tabs.addTab(self.calendar_tab, 'Calendar')

        self.setup_worker_tab()
        self.setup_task_tab()
        self.setup_calendar_tab()

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

        # Инициализация QComboBox с работниками
        self.task_worker_input = QComboBox()

        # Инициализация QLineEdit для заголовка задачи
        self.task_title_input = QLineEdit()

        # Инициализация QDateEdit для даты начала
        self.task_start_input = QDateEdit()
        self.task_start_input.setDisplayFormat('dd.MM.yyyy')  # Установите формат отображения
        self.task_start_input.setCalendarPopup(True)  # Включить календарь
        self.task_start_input.setDate(QDate.currentDate())  # Установить текущую дату

        # Инициализация QDateEdit для даты конца
        self.task_end_input = QDateEdit()
        self.task_end_input.setDisplayFormat('dd.MM.yyyy')  # Установите формат отображения
        self.task_end_input.setCalendarPopup(True)  # Включить календарь
        self.task_end_input.setDate(QDate.currentDate())  # Установить текущую дату

        # Инициализация QComboBox для статуса задачи
        self.task_status_input = QComboBox()
        self.task_status_input.addItems(['В процессе', 'Выполнено', 'Приостановлена'])

        # Добавление виджетов в форму
        self.task_form.addRow(QLabel('Worker:'), self.task_worker_input)
        self.task_form.addRow(QLabel('Title:'), self.task_title_input)
        self.task_form.addRow(QLabel('Start Date:'), self.task_start_input)
        self.task_form.addRow(QLabel('End Date:'), self.task_end_input)
        self.task_form.addRow(QLabel('Status:'), self.task_status_input)

        # Инициализация кнопок для задач
        self.task_buttons_layout = QVBoxLayout()
        self.add_task_button = QPushButton('Add Task')
        self.remove_task_button = QPushButton('Remove Task')
        self.task_buttons_layout.addWidget(self.add_task_button)
        self.task_buttons_layout.addWidget(self.remove_task_button)

        # Добавление формы и кнопок на вкладку задач
        self.task_layout.addLayout(self.task_form)
        self.task_layout.addLayout(self.task_buttons_layout)

        self.task_tab.setLayout(self.task_layout)

        # Подключение кнопок к методам
        self.add_task_button.clicked.connect(self.add_task)
        self.remove_task_button.clicked.connect(self.remove_task)

    def update_data(self):
        if self.tabs.currentIndex() == 0:
            self.load_workers()
        elif self.tabs.currentIndex() == 1:
            workers = self.load_workers()
            self.task_worker_input.clear()
            self.task_worker_input.addItems([w[1] for w in workers])
            self.load_tasks()
        elif self.tabs.currentIndex() == 2:
            self.load_calendar_tasks()

    def add_worker(self):
        try:
            name = self.worker_name_input.text()
            if name:
                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO workers (name, color) VALUES (?, ?)', (name, 'white'))
                conn.commit()
                conn.close()
                self.worker_name_input.clear()
                self.update_data()
            else:
                print("Worker name is empty.")
        except Exception as e:
            print(f"Error adding worker: {e}")

    def remove_worker(self):
        try:
            selected_items = self.worker_list.selectedItems()
            if selected_items:
                worker_name = selected_items[0].text()
                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM workers WHERE name = ?', (worker_name,))
                conn.commit()
                conn.close()
                self.update_data()
            else:
                print("No worker selected.")
        except Exception as e:
            print(f"Error removing worker: {e}")

    def load_workers(self):
        try:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM workers')
            workers = cursor.fetchall()
            conn.close()
            self.worker_list.clear()
            for worker in workers:
                self.worker_list.addItem(worker[1])
            print(f"Loaded workers: {workers}")
            return workers
        except Exception as e:
            print(f"Error loading workers: {e}")
            return []

    def add_task(self):
        try:
            worker_name = self.task_worker_input.currentText()
            title = self.task_title_input.text()
            start_date = self.task_start_input.date().toString('yyyy-MM-dd')
            end_date = self.task_end_input.date().toString('yyyy-MM-dd')
            status = self.task_status_input.currentText()

            if worker_name and title and start_date and end_date and status:
                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM workers WHERE name = ?', (worker_name,))
                worker_id = cursor.fetchone()[0]

                cursor.execute('''
                    INSERT INTO tasks (worker_id, title, start_date, end_date, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (worker_id, title, start_date, end_date, status))
                conn.commit()
                conn.close()
                self.update_data()
            else:
                print("Some task information is missing.")
        except Exception as e:
            print(f"Error adding task: {e}")

    def remove_task(self):
        try:
            selected_items = self.task_table.selectedItems()
            if selected_items:
                task_id = selected_items[0].data(Qt.UserRole)
                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                conn.commit()
                conn.close()
                self.update_data()
            else:
                print("No task selected.")
        except Exception as e:
            print(f"Error removing task: {e}")

    def load_tasks(self):
        try:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tasks.id, workers.name, tasks.title, tasks.start_date, tasks.end_date, tasks.status
                FROM tasks
                JOIN workers ON tasks.worker_id = workers.id
            ''')
            tasks = cursor.fetchall()
            conn.close()

            self.task_table.clear()
            self.task_table.setRowCount(len(tasks))
            self.task_table.setColumnCount(6)
            self.task_table.setHorizontalHeaderLabels(['ID', 'Worker', 'Title', 'Start Date', 'End Date', 'Status'])

            status_items = ['В процессе', 'Выполнено', 'Приостановлена']

            for row_index, task in enumerate(tasks):
                for col_index, data in enumerate(task):
                    if col_index == 5:  # Столбец статуса
                        combo_box = QComboBox()
                        combo_box.addItems(status_items)
                        combo_box.setCurrentText(data)
                        combo_box.currentIndexChanged.connect(lambda index, row=row_index: self.update_task_status(row, status_items[index]))
                        self.task_table.setCellWidget(row_index, col_index, combo_box)
                    else:
                        item = QTableWidgetItem(str(data))
                        if col_index == 0:
                            item.setData(Qt.UserRole, task[0])
                        self.task_table.setItem(row_index, col_index, item)

            self.task_table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error loading tasks: {e}")

    def update_task_status(self, row, new_status):
        try:
            task_id = self.task_table.item(row, 0).data(Qt.UserRole)
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, task_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating task status: {e}")
    def setup_calendar_tab(self):
        self.calendar_layout = QVBoxLayout()
        self.calendar = CustomCalendarWidget()
        self.calendar_layout.addWidget(self.calendar)
        self.calendar_tab.setLayout(self.calendar_layout)
        self.load_calendar_tasks()

    def load_calendar_tasks(self):
        try:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tasks.title, tasks.start_date, tasks.end_date, workers.name, tasks.status
                FROM tasks
                JOIN workers ON tasks.worker_id = workers.id
            ''')
            tasks = cursor.fetchall()
            conn.close()

            self.calendar.task_data = []  # Очистка старых задач
            for task in tasks:
                title, start_date, end_date, worker_name, status = task
                start_qdate = QDate.fromString(start_date, 'yyyy-MM-dd')
                end_qdate = QDate.fromString(end_date, 'yyyy-MM-dd')
                color = self.get_status_color(status)
                # Теперь передаем название задачи и имя работника
                self.calendar.mark_calendar_dates(start_qdate, end_qdate, color, title, worker_name)
        except Exception as e:
            print(f"Error loading calendar tasks: {e}")

    def get_status_color(self, status):
        if status == 'В процессе':
            return 'yellow'
        elif status == 'Выполнено':
            return 'green'
        elif status == 'Приостановлена':
            return 'red'
        else:
            return 'white'


class CustomCalendarWidget(QCalendarWidget):
    def __init__(self):
        super().__init__()
        self.task_data = []

    def mark_calendar_dates(self, start_date, end_date, color, worker_name):
        self.task_data.append((start_date, end_date, color, worker_name))
        self.updateCells()

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)

        y_offset = 2
        for task in self.task_data:
            start_date, end_date, color, worker_name = task
            if start_date <= date <= end_date:
                painter.save()
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(color)))
                circle_diameter = 10
                circle_x = rect.left() + 2
                circle_y = rect.top() + y_offset
                painter.drawEllipse(circle_x, circle_y, circle_diameter, circle_diameter)
                painter.restore()

                painter.setPen(Qt.black)
                text_x = circle_x + circle_diameter + 2
                text_y = circle_y + circle_diameter - 2
                painter.drawText(text_x, text_y, worker_name)

                y_offset += circle_diameter + 5


class CustomCalendarWidget(QCalendarWidget):
    def __init__(self):
        super().__init__()
        self.task_data = []

    def mark_calendar_dates(self, start_date, end_date, color, task_title, worker_name):
        self.task_data.append((start_date, end_date, color, task_title, worker_name))
        self.updateCells()

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)

        y_offset = 2
        for task in self.task_data:
            start_date, end_date, color, task_title, worker_name = task
            if start_date <= date <= end_date:
                painter.save()
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(color)))
                circle_diameter = 10
                circle_x = rect.left() + 2
                circle_y = rect.top() + y_offset
                painter.drawEllipse(circle_x, circle_y, circle_diameter, circle_diameter)
                painter.restore()

                painter.setPen(Qt.black)
                text_x = circle_x + circle_diameter + 2
                text_y = circle_y + circle_diameter - 2
                text = f"{task_title} ({worker_name})"
                painter.drawText(text_x, text_y, text)

                y_offset += circle_diameter + 5  # Увеличиваем y_offset для следующего текста

if __name__ == '__main__':
    create_tables()
    update_existing_workers_with_color()
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
