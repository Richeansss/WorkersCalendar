import re
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFormLayout, QLineEdit, QLabel, QTabWidget, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
    QCalendarWidget, QTextBrowser, QTableWidget, QHeaderView
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget
import html


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Менеджер задач')
        self.setGeometry(100, 100, 1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.worker_tab = QWidget()
        self.task_tab = QWidget()
        self.calendar_tab = QWidget()

        self.tabs.addTab(self.worker_tab, 'Работники')
        self.tabs.addTab(self.task_tab, 'Задачи')
        self.tabs.addTab(self.calendar_tab, 'Календарь')

        self.setup_worker_tab()
        self.setup_task_tab()
        self.setup_calendar_tab()

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
        self.worker_form.addRow(QLabel('Имя работника:'), self.worker_name_input)

        self.worker_buttons_layout = QVBoxLayout()
        self.add_worker_button = QPushButton('Добавить работника')
        self.remove_worker_button = QPushButton('Удалить работника')
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
        self.add_task_button = QPushButton('Добавить задачу')
        self.remove_task_button = QPushButton('Удалить задачу')
        self.task_buttons_layout.addWidget(self.add_task_button)
        self.task_buttons_layout.addWidget(self.remove_task_button)

        self.task_layout.addLayout(self.task_form)
        self.task_layout.addLayout(self.task_buttons_layout)

        self.task_tab.setLayout(self.task_layout)

        # Connect buttons to methods
        self.add_task_button.clicked.connect(self.add_task)
        self.remove_task_button.clicked.connect(self.remove_task)

    def setup_calendar_tab(self):
        self.calendar_layout = QVBoxLayout()

        # Navigation Buttons
        self.prev_month_button = QPushButton('<< Предыдущий  месяц')
        self.next_month_button = QPushButton('Следующий месяц >>')
        self.calendar_layout.addWidget(self.prev_month_button)
        self.calendar_layout.addWidget(self.next_month_button)

        # Calendar Table
        self.calendar_table = QTableWidget(6, 7)
        self.calendar_table.setHorizontalHeaderLabels(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])
        self.calendar_table.horizontalHeader().setStretchLastSection(True)
        self.calendar_table.verticalHeader().setVisible(False)
        self.calendar_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.calendar_table.setSelectionMode(QTableWidget.NoSelection)
        self.calendar_layout.addWidget(self.calendar_table)

        self.prev_month_button.clicked.connect(self.show_prev_month)
        self.next_month_button.clicked.connect(self.show_next_month)

        self.current_date = QDate.currentDate()
        self.show_month(self.current_date.year(), self.current_date.month())

        self.calendar_tab.setLayout(self.calendar_layout)

    def initialize_task_form(self):
        self.task_start_input.setDisplayFormat('dd.MM.yyyy')
        self.task_start_input.setCalendarPopup(True)
        self.task_start_input.setDate(QDate.currentDate())

        self.task_end_input.setDisplayFormat('dd.MM.yyyy')
        self.task_end_input.setCalendarPopup(True)
        self.task_end_input.setDate(QDate.currentDate())

        self.task_status_input.addItems(['В прогрессе', 'Завершена', 'Остановлена'])

        self.task_form.addRow(QLabel('Рабочий:'), self.task_worker_input)
        self.task_form.addRow(QLabel('Название задачи:'), self.task_title_input)
        self.task_form.addRow(QLabel('Дата начала:'), self.task_start_input)
        self.task_form.addRow(QLabel('Дата конца:'), self.task_end_input)
        self.task_form.addRow(QLabel('Статус:'), self.task_status_input)

    def update_data(self):
        current_index = self.tabs.currentIndex()
        if current_index == 0:  # Workers tab
            self.load_workers()
        elif current_index == 1:  # Tasks tab
            workers = self.load_workers()  # Update worker combo box
            self.task_worker_input.clear()
            self.task_worker_input.addItems([w[1] for w in workers])
            self.load_tasks()
        elif current_index == 2:  # Calendar tab
            self.show_month(self.current_date.year(), self.current_date.month())

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
                print(f"Ошибка при добавлении работника: {e}")
        else:
            print("Имя работника не заполнено.")

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
                    print(f"Не найден работник с именем: {selected_worker}")
            except Exception as e:
                print(f"Ошибка удаления работника: {e}")
        else:
            print("Работник не выбран.")

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
                print(f"Ошибка при добавлении задачи: {e}")
        else:
            print("Работник не выбран.")

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
                print(f"Ошибка при удалении задачи: {e}")
        else:
            print("Задача не выбрана.")

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
            print(f"Ошибка при загрузки таблицы Работники: {e}")
            return []

    def load_tasks(self):
        try:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT tasks.id, workers.name, tasks.title, tasks.start_date, tasks.end_date, tasks.status '
                               'FROM tasks JOIN workers ON tasks.worker_id = workers.id')
                tasks = cursor.fetchall()

            self.task_table.setRowCount(0)
            self.task_table.setColumnCount(6)
            self.task_table.setHorizontalHeaderLabels(['ID', 'Worker', 'Title', 'Start Date', 'End Date', 'Status'])
            self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for task in tasks:
                row_position = self.task_table.rowCount()
                self.task_table.insertRow(row_position)
                for column, item in enumerate(task):
                    self.task_table.setItem(row_position, column, QTableWidgetItem(str(item)))
        except Exception as e:
            print(f"Ошибка при загрузке таблицы Задачи: {e}")

    def strip_html_tags(self, text):
        """Удаляет все HTML-теги из строки и декодирует сущности."""
        # Удаляем HTML-теги
        clean_text = re.sub(r'<[^>]+>', '', text)
        # Декодируем сущности HTML
        print(clean_text)
        return html.unescape(clean_text)


    def show_month(self, year, month):
        self.current_date = QDate(year, month, 1)
        days_in_month = self.current_date.daysInMonth()
        first_day_of_month = self.current_date.dayOfWeek() - 1  # Monday = 0, Sunday = 6
        self.calendar_table.clearContents()

        # Заполняем календарь числами и задачами
        for i in range(1, days_in_month + 1):
            day_date = QDate(year, month, i)
            tasks = self.get_tasks_for_date(day_date.toString('yyyy-MM-dd'))

            # Формируем строку с датой и задачами
            task_str = f"{i}"
            tooltip_str = ""
            if tasks:
                task_details = "\n".join([
                    f"{get_status_color_dot(task[5])} {task[1]}: {task[2]} ({task[5]})"
                    for task in tasks
                ])  # Добавлено имя работника и цветная точка
                task_str = f"{i}\n{self.strip_html_tags(task_details)}"  # Убираем HTML-код из текста
                tooltip_str = f'<div style="white-space: pre-line;">{task_details}</div>'  # Оставляем HTML в тултипе

            # Создаем и устанавливаем элемент
            day_item = QTableWidgetItem(task_str)
            if tooltip_str:
                day_item.setToolTip(tooltip_str)  # Устанавливаем тултип

            # Изменяем цвет текста в зависимости от статуса первой задачи
            if tasks:
                status_color = {
                    "завершена": "green",
                    "приостановлена": "yellow",
                    "в процессе": "blue"
                }.get(tasks[0][5], "black")  # По умолчанию - черный цвет
                day_item.setForeground(QColor(status_color))

            row = (i + first_day_of_month - 1) // 7
            col = (i + first_day_of_month - 1) % 7
            self.calendar_table.setItem(row, col, day_item)

        # Настройка размера заголовков таблицы
        self.calendar_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.calendar_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.calendar_table.resizeRowsToContents()  # Автома

    def get_tasks_for_date(self, date_str):
        try:
            with sqlite3.connect('tasks.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT tasks.id, workers.name, tasks.title, tasks.start_date, tasks.end_date, tasks.status '
                    'FROM tasks JOIN workers ON tasks.worker_id = workers.id '
                    'WHERE tasks.start_date <= ? AND tasks.end_date >= ?',
                    (date_str, date_str)
                )
                tasks = cursor.fetchall()
                return tasks
        except Exception as e:
            print(f"Error fetching tasks for date {date_str}: {e}")
            return []


    def show_prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.show_month(self.current_date.year(), self.current_date.month())

    def show_next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.show_month(self.current_date.year(), self.current_date.month())

def create_color_dot_pixmap(color, size=10):
    """Создает QPixmap с точкой нужного цвета."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)  # Делает фон прозрачным
    painter = QPainter(pixmap)
    painter.setBrush(QColor(color))
    painter.drawEllipse(0, 0, size, size)  # Рисуем круг (точку)
    painter.end()
    return pixmap

def get_status_color_dot(status):
    color_map = {
        "Завершена": "green",
        "Остановлена": "yellow",
        "В процессе": "blue"  # Придуманный статус для "в процессе"
    }
    color = color_map.get(status, "gray")  # По умолчанию - серый цвет
    return f'<span style="color:{color};">&#9679;</span>'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())