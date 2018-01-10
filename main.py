import sys
import os
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox

from front import Ui_MainWindow


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
            with open(path[0], newline='') as csv_file:
                self.populate_table(csv_file)

    def populate_table(self, csv_file):
        my_file = csv.reader(csv_file, delimiter=';', quotechar="\"")
        headers = next(my_file)
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(len(headers))
        for index, header in enumerate(headers):
            # TODO polskie znaki wysadzają QTableWidget
            self.ui.tableWidget.setHorizontalHeaderItem(index, QTableWidgetItem(header))
        for row_data in my_file:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            self.ui.tableWidget.setColumnCount(len(row_data))
            for column, stuff in enumerate(row_data):
                item = QTableWidgetItem(stuff)
                self.ui.tableWidget.setItem(row, column, item)

    def evaluate(self):
        print(self.ui.ratioLineEdit.text())
        number = self.ui.ratioLineEdit.text()
        try:
            number = float(number)
        except Exception:
            QMessageBox.about(self, 'Błąd', 'Wprowadź liczbę zmiennoprzecinkową')
            return
        self.insert_result()

    def insert_result(self):
        self.ui.metacriterionLineEdit.setText("ABCDEFG")

        self.ui.shareholdingTable.setRowCount(0)
        self.ui.shareholdingTable.setColumnCount(2)
        self.ui.shareholdingTable.insertRow(0)
        self.ui.shareholdingTable.setItem(0, 0, QTableWidgetItem('test'))
        self.ui.shareholdingTable.setItem(0, 1, QTableWidgetItem('test'))


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
