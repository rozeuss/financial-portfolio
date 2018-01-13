import sys
import os
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox

from front import Ui_MainWindow
from back import calculate


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.statusbar.showMessage("Zadanie optymalizacji wielokryterialnej z wykorzystaniem funkcji metakryterium")
        self.ui.shareholdingTable.horizontalScrollBar().setDisabled(True)
        self.ui.shareholdingTable.verticalHeader().setVisible(False)
        self.ui.chooseFileButton.clicked.connect(self.open_sheet)
        self.ui.evaluateButton.clicked.connect(self.evaluate)

    def open_sheet(self):
        path = QFileDialog.getOpenFileName(self, 'Wybierz plik CSV', os.getenv('HOME'), 'CSV(*.csv)')
        if path[0] != '':
            self.ui.filePathLineEdit.setText(path[0])
            with open(path[0], newline='', encoding='utf_8') as csv_file:
                self.populate_table(csv_file)

    def populate_table(self, csv_file):
        my_file = csv.reader(csv_file, delimiter=';')
        data = []
        headers = next(my_file)
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(len(headers))
        for index, header in enumerate(headers):
            self.ui.tableWidget.setHorizontalHeaderItem(index, QTableWidgetItem(header))
        for row_data in my_file:
            data.append(row_data)
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            self.ui.tableWidget.setColumnCount(len(row_data))
            for column, stuff in enumerate(row_data):
                item = QTableWidgetItem(stuff)
                self.ui.tableWidget.setItem(row, column, item)
        global data_first
        data_first = [float(item[1]) for item in data]
        global data_second
        data_second = [float(item[2]) for item in data]

    def evaluate(self):
        number = self.ui.ratioLineEdit.text()
        try:
            number = float(number)
        except Exception:
            QMessageBox.about(self, 'Błąd', 'Wprowadź liczbę zmiennoprzecinkową.')
            return
        result = calculate(data_first, data_second, number)
        self.insert_result(result)

    def insert_result(self, result):
        self.ui.metacriterionLineEdit.setText(str(result[0]))
        self.ui.shareholdingTable.setRowCount(0)
        self.ui.shareholdingTable.setColumnCount(2)
        self.ui.shareholdingTable.insertRow(0)
        self.ui.shareholdingTable.insertRow(1)
        self.ui.shareholdingTable.setItem(0, 0, QTableWidgetItem(self.ui.tableWidget.horizontalHeaderItem(1).text()))
        self.ui.shareholdingTable.setItem(0, 1, QTableWidgetItem(str(result[1])))
        self.ui.shareholdingTable.setItem(1, 0, QTableWidgetItem(self.ui.tableWidget.horizontalHeaderItem(2).text()))
        self.ui.shareholdingTable.setItem(1, 1, QTableWidgetItem(str(result[2])))


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
