from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, \
    QGridLayout, QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QComboBox, QToolBar, QStatusBar, QMessageBox

from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3
from datetime import datetime


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

         # Create Menu
        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert_record)
        file_menu_item.addAction(add_student_action)

        search_action = QAction(QIcon("icons/search.png"), 'Search', self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(('Id', "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Main Toolbar Layout.
        toolbar = QToolBar()
        toolbar.setMovable(True)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)
        self.addToolBar(toolbar)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Detect a click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        results = connection.execute('SELECT * FROM students')
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(results):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number,
                                   column_number,
                                   QTableWidgetItem(str(data)))
        connection.close()

    def insert_record(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        search_dialog = SearchDialog()
        search_dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutMessageBox()
        dialog.exec()


class AboutMessageBox(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Student Updater")
        content = """
        This app was created during the course "The Python Mega Course" 
        Feel free to modify and re-use this app. 
        """
        self.setText(content)


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student")


        index = main_window.table.currentRow()
        self.record_id = main_window.table.item(index, 0).text()

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete.")
        yes = QPushButton("Yes")
        yes.clicked.connect(self.delete_record)
        no = QPushButton('No')
        no.clicked.connect(self.close)

        layout.addWidget(confirmation, 0, 0 , 1, 2)
        layout.addWidget(yes, 1, 0, 1, 1)
        layout.addWidget(no, 1,1, 1, 1)
        self.setLayout(layout)

    def delete_record(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        sql = "DELETE from students WHERE id = ?"
        cursor.execute(sql, (self.record_id, ))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh Main Table
        main_window.load_data()
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("success")
        confirmation_widget.setText('The record was deleted successuflly!')
        confirmation_widget.exec()



class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()
        subject = main_window.table.item(index, 2).text()
        mobile = main_window.table.item(index, 3).text()
        self.student_id = main_window.table.item(index, 0).text()
        layout = QVBoxLayout()

        # Add Student Name Widget
        self.student_name = QLineEdit(student_name)
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ['Biology', "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(subject)
        layout.addWidget(self.course_name)

        # Add Student number widget
        self.student_phone = QLineEdit(mobile)
        self.student_phone.setPlaceholderText("Phone")
        layout.addWidget(self.student_phone)

        # Add a submit button
        submit_button = QPushButton("Save Changes")
        submit_button.clicked.connect(self.update_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        sql = "UPDATE students SET name=?, course = ?, mobile = ? WHERE id = ?"
        cursor.execute(sql, (self.student_name.text(),
                             self.course_name.itemText(self.course_name.currentIndex()),
                             self.student_phone.text(),
                             self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh Main Table
        main_window.load_data()
        self.close()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add Student Name Widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ['Biology', "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add Student number widget
        self.student_phone = QLineEdit()
        self.student_phone.setPlaceholderText("Phone")
        layout.addWidget(self.student_phone)

        # Add a submit button
        submit_button = QPushButton("Save")
        submit_button.clicked.connect(self.add_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.student_phone.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        sql = "INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)"
        cursor.execute(sql, (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Name")
        layout.addWidget(self.search_box)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_names)
        layout.addWidget(self.search_button)

        self.setLayout(layout)

    def search_names(self):
        name = self.search_box.text()
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        sql = ("SELECT * FROM students WHERE name = ?")
        results = cursor.execute(sql, (name, ))
        rows = list(results)
        print(rows)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    main_window.load_data()
    sys.exit(app.exec())
