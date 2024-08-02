import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget, QFormLayout, \
    QLineEdit, QLabel, QTabWidget, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem
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

        # Подключаем сигнал переключения вкладок к методу обновления данных
        self.tabs.currentChanged.connect(self.update_data)

        # Изначальная загрузка данных
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

        # Подключаем кнопки к методам
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
        # Обновление данных на активной вкладке
        if self.tabs.currentIndex() == 0:  # Вкладка работников
            self.load_workers()
        elif self.tabs.currentIndex() == 1:  # Вкладка задач
            workers = self.load_workers()  # Для обновления данных в QComboBox
            self.task_worker_input.clear()
            self.task_worker_input.addItems([w[1] for w in workers])
            self.load_tasks()

    def add_worker(self):
        try:
            name = self.worker_name_input.text()
            if name:
                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO workers (name) VALUES (?)', (name,))
                conn.commit()
                conn.close()
                self.worker_name_input.clear()  # Очистить поле ввода
                self.update_data()  # Обновить данные на вкладке работников
            else:
                print("Worker name is empty.")  # Отладочный вывод
        except Exception as e:
            print(f"Error adding worker: {e}")

    def remove_worker(self):
        try:
            selected_items = self.worker_list.selectedItems()
            if selected_items:
                selected_worker = selected_items[0].text()
                worker_id = [w[0] for w in self.load_workers() if w[1] == selected_worker][0]
                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM workers WHERE id = ?', (worker_id,))
                conn.commit()
                conn.close()
                self.update_data()  # Обновить данные на вкладке работников
            else:
                print("No worker selected.")  # Отладочный вывод
        except Exception as e:
            print(f"Error removing worker: {e}")

    def add_task(self):
        try:
            worker_name = self.task_worker_input.currentText()
            title = self.task_title_input.text()
            start_date = self.task_start_input.date().toString('yyyy-MM-dd')  # Форматируем дату
            end_date = self.task_end_input.date().toString('yyyy-MM-dd')  # Форматируем дату
            status = self.task_status_input.currentText()  # Получаем выбранный статус из QComboBox

            workers = self.load_workers()
            worker_id = [w[0] for w in workers if w[1] == worker_name]

            if not worker_id:
                print(f"No worker found with name: {worker_name}")
                return

            worker_id = worker_id[0]
            if title and worker_id:
                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO tasks (worker_id, title, start_date, end_date, status) VALUES (?, ?, ?, ?, ?)',
                               (worker_id, title, start_date, end_date, status))
                conn.commit()
                conn.close()
                self.task_title_input.clear()
                self.task_status_input.setCurrentIndex(0)  # Сбросить выбор статуса на первый элемент
                self.update_data()  # Обновить данные на вкладке задач
            else:
                print("Title or worker ID is empty.")
        except Exception as e:
            print(f"Error adding task: {e}")

    def remove_task(self):
        try:
            selected_items = self.task_table.selectedItems()
            if selected_items:
                # Получаем ID задачи из первой ячейки выбранной строки
                selected_row = selected_items[0].row()
                task_id = self.task_table.item(selected_row, 0).text()  # ID задачи в первом столбце

                conn = sqlite3.connect('tasks.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                conn.commit()
                conn.close()
                self.update_data()  # Обновить данные на вкладке задач
            else:
                print("No task selected.")  # Отладочный вывод
        except Exception as e:
            print(f"Error removing task: {e}")


    def load_workers(self):
        try:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM workers')
            workers = cursor.fetchall()
            conn.close()
            self.worker_list.clear()
            for worker in workers:
                self.worker_list.addItem(worker[1])
            return workers
        except Exception as e:
            print(f"Error loading workers: {e}")
            return []

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

            self.task_table.setRowCount(len(tasks))
            self.task_table.setColumnCount(6)  # Устанавливаем количество столбцов

            # Устанавливаем заголовки столбцов
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
