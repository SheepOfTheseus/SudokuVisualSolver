#current goals:
#1. make color feedback for solving process
    #-add method inactivity increment
    #-add method inactivity reset
    #-add method inactivity to color
    #-add color variables to style application
#2. add more GUI elements for more control

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout
import sys

from PyQt5.QtGui import QFont, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, center, reset, right

#window dimensions
HEIGHT = 600
WIDTH = 600

#a constant for oob and win conditions
GRID_SIDE_MAX = 8

#total steps fyi
STEPS_COUNT = 0

#temp solution not to enter values manualy
imp_grid = [
    [0,0,8,0,2,4,0,6,0],
    [2,0,0,0,8,0,4,3,0],
    [0,0,0,1,0,0,0,0,0],
    [1,0,0,0,0,7,0,0,5],
    [7,3,0,5,0,1,0,9,6],
    [6,0,0,2,0,0,0,0,4],
    [0,0,0,0,0,6,0,0,0],
    [0,1,3,0,5,0,0,0,2],
    [0,5,0,7,9,0,1,0,0]
    ]

#GUI start
app = QApplication(sys.argv) # < initiates application, allowing for the GUI to be displayed

#class description for the main window object
class w(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.title = "Sudoku visual solver"
        self.InitWindow()
    
    #main window startup procedure
    def InitWindow(self) -> None:
        self.setWindowTitle(self.title)                                             # < sets main window title
        self.setFixedSize(HEIGHT, WIDTH)                                            # < makes main window of a fixed size
        #self.setStyleSheet('QLabel {background-color: #252525; color: #ffff00;}')   # < sets style for the cells in the window <-------------junk for later
        self.show()                                                                 # < makes the main window appear on the screen

    #events for when a key is pressed
    def keyPressEvent(self, e) -> None:
        if e.key() == Qt.Key_Space:
            GRID.step()
            GRID.refresh_grid()
        if e.key() == Qt.Key_Escape:
            self.close()

    #2 vertical and 2 horizontal lines subdividing the 9x9 grid into 9 squares
    def paintEvent(self,event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white,  2, Qt.SolidLine))
        painter.drawLine(round(HEIGHT/3), 0, round(HEIGHT/3), WIDTH)
        painter.drawLine(round(HEIGHT/3*2), 0, round(HEIGHT/3*2), WIDTH)
        painter.drawLine(0, round(WIDTH/3), HEIGHT, round(WIDTH/3))
        painter.drawLine(0, round(WIDTH/3*2), HEIGHT, round(WIDTH/3*2))

#labels, that are used to show numbers within the grid
class grid_label(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setFont(QFont('Times font',20))
        self.setAlignment(Qt.AlignCenter)

#grid, central element, containing 81 cells in a 9x9 square pattern
class gridclass():
    def __init__(self) -> None:
        self.main_grid = []         # < initiation of the to be list of 9 rows, each with 9 cells
        self.solving_next_y = 0     # < coordinates of the to be solved cell stored between steppes
        self.solving_next_x = 0     # < ^^^
        self.solved = False         # < switch to be toggled to True when the grid will be solved
        self.l = QGridLayout()      # < layout that will store the position of the GUI elements in a 9x9 grid
        self.wid = QWidget()        # < widget containing all of the GUI elements of the grid
        self.grid_reset()           # < resets the grid, and fills it with 81 cell objects
        self.wid.setLayout(self.l)  # < sets layout l as the layout for the widget wid 

    #resets the grid, and fills it with 81 cell objects
    def grid_reset(self) -> None:
        self.main_grid = []
        for y in range(9):
            row = []
            for x in range(9):
                c = cell(y,x)
                row.append(c)
            self.main_grid.append(row)

    #import values from 9x9 integer list
    def imp_from_list(self, l:list) -> None:
        self.grid_reset()
        self.solved = False
        for row in self.main_grid:
            for cell in row:
                cell.value = l[cell.coord_y][cell.coord_x]
                if cell.value == 0:
                    cell.changeble = True
                else:
                    cell.changeble = False

    #refreshed full grid of labels and assigns them to the layout assigned to the gridclass
    def refresh_grid(self) -> None:
        for row in self.main_grid:
            for cell in row:
                cell.set_label()
                self.l.addWidget(cell.label,cell.coord_y,cell.coord_x)

    #refreshes one cell and reassigns it to the layout assigned to the gridclass
    def refresh_cell(self, y: int,x: int) -> None:
        self.main_grid[y][x].set_label()
        self.l.addWidget(self.main_grid[y][x].label,y,x)

    #main function driving the process of gradual solving
    #steps through the grid back and forth solving it one cell at a time
    def step(self) -> bool:
        if not self.solved: #<-------------------------------WARNING! temp solution fix later(should be elseware)
            if self.solving_next_y > 8: #end of operation condition, not to call elements oob of the main_grid
                self.solved = True
            if self.main_grid[self.solving_next_y][self.solving_next_x].solve():
                self.next_cell(1)
            else:
                self.next_cell(-1)

    #moves currently solved cell on demand of the step function
    #direction can be 1 or -1, 1 moves the cell forwards, -1 backwards
    def next_cell(self, direction: int) -> None:
        self.solving_next_x += direction
        self.overflow_rectification()
        self.skip_unchangable(direction)

    #converts linear movement through a line into cyclic movement through a 9x9 plane
    def overflow_rectification(self) -> None:
        if self.solving_next_x > 8:
            self.solving_next_x = 0
            self.solving_next_y += 1
        elif self.solving_next_x < 0:
            self.solving_next_x = 8
            self.solving_next_y -= 1

    #recursively calls movement function(next_cell) if current cell is unchangable
    def skip_unchangable(self, momentum: int) -> None:
        if self.solving_next_y < 9: #<----------------------------redundant oob check, revisit later
            if not self.main_grid[self.solving_next_y][self.solving_next_x].changeble:
                self.next_cell(momentum)
#cell class description
class cell():
    def __init__(self, y: int, x: int) -> None:
        self.value = 0                  # < value of the cell (1-9)
        self.changeble = True           # < this tracks the possibility to change the value during backtrack
        self.coord_y = y                # < coordinates of the current cell
        self.coord_x = x                # < coordinates of the current cell
        self.label = grid_label()       # < element containing visual represetation of the current cell
        self.inactive = 0
    
    #checks if object is self
    def not_itself(self,cell:object) -> bool:
        if cell.coord_y == self.coord_y and cell.coord_x == self.coord_x:
            return(False)
        else:
            return(True)

    #checks if another cell has same value
    def value_check(self,cell:object) -> bool:
        if cell.value == self.value and self.not_itself(cell):
            return(True)

    #checks if there are cells with values matching the value of the current cell..
    #in a row, column and metacell(3x3 square) containing current cell
    def check_constraint(self) -> bool:
        #check row
        for cell in GRID.main_grid[self.coord_y]:
            if self.value_check(cell):
                return(False)
        #check column
        for row in GRID.main_grid:
            if self.value_check(row[self.coord_x]):
                return(False)
        #check metacell
        m_x = self.coord_x // 3 * 3
        m_y = self.coord_y // 3 * 3
        for row in GRID.main_grid[m_y:m_y+2]:
            for cell in row[m_x:m_x+2]:
                if self.value_check(cell):
                    return(False)
        return(True)

    #increments value of the cell
    def increment_value(self) -> bool:
        self.value += 1
        if self.value > 9:
            self.value = 0
            return(False)
        else:
            return(True)
   
    #solves this specific cell
    def solve(self) -> bool:
        while self.increment_value():
            if self.check_constraint():
               # GRID.refresh_cell(self.coord_y,self.coord_y)
                return(True)
        #GRID.refresh_cell(self.coord_y,self.coord_y)
        return(False)

    #assigns a string character to the associated label converted from the value of the cell
    def set_label(self) -> None: #<-------------------------------------------------------------------------set color for different types of cells
        if not self.changeble:
            self.label.setStyleSheet('QLabel {background-color: #252525; color: #00ffaa;}')   # < sets style for the cells in the window
        else:
            self.label.setStyleSheet('QLabel {background-color: #252525; color: #ffff00;}')   # < sets style for the cells in the window
        if self.value != 0:
            self.label.setText(str(self.value))
        else:
            self.label.setText('')

#initializing the 9x9 grid
GRID = gridclass()

GRID.imp_from_list(imp_grid)
GRID.refresh_grid()

window = w()
window.setCentralWidget(GRID.wid)

sys.exit(app.exec()) #end



"""#constraint check
def check_constraint(y: int, x: int, choice: int) -> bool:
    global GRID
    #check row
    for i, cell in enumerate(GRID[y]):
        if cell == choice and i != x:
            return(False)
    #check column
    for i, row in enumerate(GRID):
        if row[x] == choice and i != y:
            return(False)
    #check metacell
    m_x = x // 3 * 3
    m_y = y // 3 * 3
    for i, row in enumerate(GRID[m_y:m_y+2]):
        for j, cell in enumerate(row[m_x:m_x+2]):
            if cell == choice and i+m_y != y and j+m_x != x:
                return(False)
    return(True)

#choice recursion
def cell_choice(y: int,x: int) -> bool:
    global GRID, STEPS, GUI_GRID
    STEPS += 1
    #check oob
    if x > GRID_SIDE:
        x = 0 
        y += 1
    
    #check win
    if y > GRID_SIDE:
        return(True) #breakout GREATSUCCESS
    
    if GRID[y][x] == 0:

        #exploring choices
        for i in POSSIBLE_CHOICES:
            #make choice
            GRID[y][x] = i
            
            t=0
            while t<10000:
                t+=1
                print(t)

            refresh_cell(y,x) #GUI refresh
            
            #check constraints
            if check_constraint(y, x, GRID[y][x]):
                if cell_choice(y, x+1):
                    return(True) #breakout SUCCESS
                
        GRID[y][x] = 0
        return(False) #breakout BACKTRACK

    else:
        if cell_choice(y, x+1):
            return(True) #breakout SUCCESS
        else:
            return(False) #breakout BACKTRACK
"""
