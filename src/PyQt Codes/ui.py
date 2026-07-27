# Imports
import random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from widgets import PixelCell, PatternPreview
from shapes import SHAPES


class MainWindow(QMainWindow):
    def __init__(self, arduino):
        super().__init__()

        self.arduino = arduino

        self.setGeometry(700, 200, 450, 700)
        self.setWindowTitle("Pixel Paint")
        self.setWindowIcon(QIcon("PixelPaint-icon.png"))

        self.paint_btn = QPushButton("Paint")
        self.random_btn = QPushButton("☻")
        self.random_btn.setObjectName("random_btn")
        self.clear_btn = QPushButton("Clear")

        self.random_btn.setToolTip("Generate a random pattern!")
        self.clear_btn.setToolTip("Turn off all LEDs")

        self.is_locked = False
        self.paint_btn.setText("Lock")
        self.paintbtntooltip()

        self.matrix_data = [[0 for col in range(8)] for row in range(8)]

        self.current_category = "All"

        self.initUI()

    def initUI(self):
        # creating a central_widget to attach everything on it
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # creating a vertical layout for everything that is going to be placed on central_widget
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # -Buttons Panel- at top
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(12, 10, 12, 0)
        # adding the 3 buttons to button_layout (panel)
        button_layout.addWidget(self.paint_btn)
        button_layout.addWidget(self.random_btn)
        button_layout.addWidget(self.clear_btn)
        # adding the button panel to main_layout
        main_layout.addLayout(button_layout)
        # connecting buttons to their functions
        self.paint_btn.clicked.connect(self.togglePaintMode)
        self.random_btn.clicked.connect(self.randomPattern)
        self.clear_btn.clicked.connect(self.clearCanvas)

        # -8x8 Grid Canvas-
        grid_widget = QWidget()
        # creating an object name used to design in qss
        grid_widget.setObjectName("matrixFrame")
        # creating a grid canvas in the matrixFrame as a layout
        display = QGridLayout(grid_widget)
        display.setContentsMargins(0, 0, 0, 0)
        display.setSpacing(1)
        display.setAlignment(Qt.AlignCenter)
        # adding the matrixFrame to main_layout
        main_layout.addWidget(grid_widget)

        # creating a 2D list to store all PixelCell objects for later access
        self.canvas_cells = []
        # creating 8 rows
        for row in range(8):
            row_cells = []
            # 8 columns in each
            for col in range(8):
                cell = PixelCell(row, col, self)

                row_cells.append(cell)
                # adding the cell to the grid layout
                display.addWidget(cell, row, col)
            # adding the completed row to the 2D canvas list
            self.canvas_cells.append(row_cells)

        # -Preview Scroll Area-
        scroll = QScrollArea()
        # creating an object name used to design in qss
        scroll.setObjectName("Scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedHeight(120)
        # creating a category panel on top
        category_panel = QHBoxLayout()

        categories = ["All", "Symbols", "Animals", "Numbers"]
        # creating a push button & connect to showCategory() for each category
        for category in categories:
            btn = QPushButton(category)
            btn.clicked.connect(lambda checked, c=category: self.updatePatternScroll(c))
            # adding category buttons made to the category panel
            category_panel.addWidget(btn)
        # adding the category panel to the main_layout
        main_layout.addLayout(category_panel)

        # creating a container for pattern previews
        container = QWidget()
        # creating an object name used to design in qss
        container.setObjectName("Container")

        # creating a horizontal layout inside the container for pattern preview buttons
        self.pattern_layout = QHBoxLayout(container)
        self.pattern_layout.setContentsMargins(5, 5, 5, 5)
        self.pattern_layout.setSpacing(10)
        # adding container to scroll area
        scroll.setWidget(container)
        # adding scroll area to main_layout
        main_layout.addWidget(scroll)
        # displaying all available patterns when the program starts (initial setting)
        self.updatePatternScroll("All")

    # removing old preview buttons before loading new ones
    def updatePatternScroll(self, category):
        while self.pattern_layout.count():
            item = self.pattern_layout.takeAt(0)

            if item.widget():
                # deleting the widget safely
                item.widget().deleteLater()

        # getting all patterns or only the selected category
        if category == "All":
            shapes = {}
            for group in SHAPES.values():
                shapes.update(group)
        else:
            shapes = SHAPES[category]
        # creating a preview button for each pattern
        for name, pattern in shapes.items():
            btn = QPushButton()
            btn.setObjectName("preview")
            btn.setFixedSize(90, 90)
            btn.setToolTip(f"Draw {name}!")
            # creating a layout inside the button to center the preview
            layout = QVBoxLayout(btn)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignCenter)
            # creating a mini LED matrix preview in each button
            preview = PatternPreview(pattern)
            layout.addWidget(preview)
            # loading the selected pattern when clicked on canvas
            btn.clicked.connect(lambda checked, s=pattern: self.loadPattern(s))

            self.pattern_layout.addWidget(btn)

    # converting the 8x8 matrix into 8 bytes for Arduino
    def getPatternBytes(self):
        pattern = []
        for row in range(8):
            # each row will become one byte
            value = 0
            for col in range(8):
                # shifting bits left to make room for the next pixel
                value <<= 1
                # adding the current pixel as the least significant bit
                value |= self.matrix_data[row][col]
            pattern.append(value)
        return pattern

    # drawing preview pattern from scroll bar on canvas & senf to arduino
    def loadPattern(self, shape):
        # preventing editing while canvas is locked
        if self.is_locked:
            return
        # extracting each bit from the selected pattern
        for row in range(8):
            for col in range(8):
                bit = (shape[row] >> (7 - col)) & 1
                self.setPixel(row, col, bit)

        self.sendToArduino()

    # freestyle painting on canvas
    def handleCellClick(self, cell):
        # ignoring clicks while canvas is locked
        if self.is_locked:
            return
        # toggling the clicked pixel
        cell.toggle()
        # updating the stored matrix data
        self.matrix_data[cell.row][cell.col] = 1 if cell.is_on else 0

        self.sendToArduino()

    # switching between locked and editable modes
    def togglePaintMode(self):
        self.is_locked = not self.is_locked
        # changing paint_btn tooltip based on flag
        self.paintbtntooltip()
        # changing paint_btn text based on flag
        if self.is_locked:
            self.paint_btn.setText("Paint")
        else:
            self.paint_btn.setText("Lock")


    def clearCanvas(self):
        # ignoring click while canvas is locked
        if self.is_locked:
            return
        # turning off every pixel on the canvas
        for row in range(8):
            for col in range(8):
                self.canvas_cells[row][col].turnOff()
                self.matrix_data[row][col] = 0

        self.sendToArduino()

    # updating both the stored matrix and the visual pixel
    def setPixel(self, row, col, state):
        self.matrix_data[row][col] = state

        if state:
            self.canvas_cells[row][col].turnOn()
        else:
            self.canvas_cells[row][col].turnOff()

    # merging all categories into a single dictionary
    def getAllShapes(self):
        all_shapes = {}
        for category in SHAPES.values():
            all_shapes.update(category)
        return all_shapes

    def randomPattern(self):
        # ignoring click while canvas is locked
        if self.is_locked:
            return

        all_shapes = self.getAllShapes()
        shape = random.choice(list(all_shapes.values()))
        for row in range(8):
            for col in range(8):
                bit = (shape[row] >> (7 - col)) & 1
                self.setPixel(row, col, bit)

        self.sendToArduino()

    # sending the current matrix state to Arduino
    def sendToArduino(self):
        # check connection
        if not self.arduino.ready:
            return

        pattern = self.getPatternBytes()
        self.arduino.send_pattern(pattern)

    def paintbtntooltip(self):
        if self.is_locked:
            self.paint_btn.setToolTip("Unlock canvas for editing")
        else:
            self.paint_btn.setToolTip("lock canvas")







