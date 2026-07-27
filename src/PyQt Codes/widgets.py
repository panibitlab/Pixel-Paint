from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor

LED_ON = QColor("#ab1d1d")
LED_OFF = QColor("#262626")


class PixelCell(QLabel):
    def __init__(self, row, col, window):
        super().__init__()

        self.window = window
        self.row = row
        self.col = col
        self.is_on = False
        self.setFixedSize(50, 50)
        self.turnOff()

    def turnOn(self):
        self.is_on = True
        self.setStyleSheet("""
            background-color: #ab1d1d;
            border: 1px solid #ff6a60;
        """)

    def turnOff(self):
        self.is_on = False
        self.setStyleSheet("""
            background-color: #1a1a1a;
            border: 1px solid #333;
        """)

    def toggle(self):
        if self.is_on:
            self.turnOff()
        else:
            self.turnOn()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window.handleCellClick(self)


class PatternPreview(QWidget):
    def __init__(self, pattern):
        super().__init__()

        self.pattern = pattern
        self.setFixedSize(75, 75)

    def paintEvent(self, event):
        painter = QPainter(self)

        size = 8
        cell_size = min(self.width() // size, self.height() // size)

        grid_size = cell_size * size

        offset_x = (self.width() - grid_size) // 2
        offset_y = (self.height() - grid_size) // 2

        for row in range(8):
            for col in range(8):
                bit = (self.pattern[row] >> (7 - col)) & 1

                x = offset_x + col * cell_size
                y = offset_y + row * cell_size

                if bit:
                    painter.fillRect(x, y, cell_size, cell_size, LED_ON)
                else:
                    painter.fillRect(x, y, cell_size, cell_size, LED_OFF)
