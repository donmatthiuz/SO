# main.py
import sys
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QComboBox, QSpinBox, QLabel, 
                             QMessageBox, QGroupBox, QGridLayout, QFrame)

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QComboBox, QSpinBox, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from src.gui.principal import SimuladorGUI


def main():
    app = QApplication(sys.argv)
    ventana = SimuladorGUI()
    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()