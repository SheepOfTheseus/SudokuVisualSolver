#current goals:
#1. make color feedback for solving process <- done
    #-add inactivity increment <- done
    #-add inactivity reset <- done
    #-add inactivity to color <- layed off
    #-add color variables to style application <- done
#1.1. un ungodlymessify the set_label func <- done
#1.2. row column metacell highlighting
#1.3. add fast solve
#2. add more GUI elements for more control

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout
import sys

from PyQt5.QtGui import QFont, QPainter, QBrush, QPen, QTextFormat
from PyQt5.QtCore import Qt, center, reset, right

# Grid widget dimensions.
HEIGHT = 600 
WIDTH = 600

STEPS_COUNT = 0

# Temp solution not to enter values manualy.
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
app = QApplication(sys.argv) 

class w(QMainWindow): 
    def __init__(self) -> None:
        super().__init__()
        self.title = "Sudoku visual solver"
        self.InitWindow()

    def InitWindow(self) -> None: 
        self.setWindowTitle(self.title)
        self.setFixedSize(HEIGHT+50, WIDTH+50)
        self.show()

    def keyPressEvent(self, e) -> None: 
        if e.key() == Qt.Key_Space:
            GRID.step()
            #GRID.one_step_solve(0,0)
            #GRID.refresh_grid()
        if e.key() == Qt.Key_Escape:
            self.close()

    def paintEvent(self,event) -> None: # 2 vertical and 2 horizontal lines subdividing the 9x9 grid into 9 squares.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white,  2, Qt.SolidLine))
        painter.drawLine(round(HEIGHT/3), 0, round(HEIGHT/3), WIDTH)
        painter.drawLine(round(HEIGHT/3*2), 0, round(HEIGHT/3*2), WIDTH)
        painter.drawLine(0, round(WIDTH/3), HEIGHT, round(WIDTH/3))
        painter.drawLine(0, round(WIDTH/3*2), HEIGHT, round(WIDTH/3*2))

class grid_label(QLabel): # Labels, that are used to show numbers within the grid.
    def __init__(self) -> None:
        super().__init__()
        self.setFont(QFont('Times font',20))
        self.setAlignment(Qt.AlignCenter)

class gridclass(): # Grid, central element, containing 81 cells in a 9x9 square pattern.
    def __init__(self) -> None:
        self.main_grid = []         # Initiation of the to be list of 9 rows, each with 9 cells.
        self.solving_next_y = 0     # Coordinates of the to be solved cell stored between steppes.
        self.solving_next_x = 0     
        self.solving_y = -1
        self.solving_x = -1
        self.solved = False         # Switch to be toggled to True when the grid will be solved.
        self.l = QGridLayout()      # Layout that will store the position of the GUI elements in a 9x9 grid.
        self.wid = QWidget()        # Widget containing all of the GUI elements of the grid.
        self.wid.setFixedSize(HEIGHT, WIDTH)  
        self.grid_reset()           # Resets the grid, and fills it with 81 cell objects.
        self.wid.setLayout(self.l)  # Sets layout l as the layout for the widget wid .

    def grid_reset(self) -> None: # Resets the grid, and fills it with 81 cell objects.
        global STEPS_COUNT
        STEPS_COUNT = 0
        self.main_grid = []
        for y in range(9):
            row = []
            for x in range(9):
                c = cell(y,x)
                row.append(c)
            self.main_grid.append(row)

    def imp_from_list(self, l:list) -> None: # Import values from 9x9 integer list.
        self.grid_reset()
        self.solved = False
        for row in self.main_grid:
            for cell in row:
                cell.value = l[cell.coord_y][cell.coord_x]
                if cell.value == 0:
                    cell.changeble = True
                else:
                    cell.changeble = False

    def refresh_grid(self) -> None: # Refreshed full grid of labels and assigns them to the layout assigned to the gridclass.
        for row in self.main_grid:
            for cell in row:
                cell.set_label()
                self.l.addWidget(cell.label,cell.coord_y,cell.coord_x)

    def refresh_cell(self, y: int,x: int) -> None: # Refreshes one cell and reassigns it to the layout assigned to the gridclass.
        self.main_grid[y][x].set_label()
        self.l.addWidget(self.main_grid[y][x].label,y,x)

    # Main function driving the process of gradual solving,
    # steps through the grid back and forth solving it one cell at a time.
    def step(self) -> bool:
        global STEPS_COUNT
        if not self.within_oob(self.solving_next_y): # End of operation condition, not to call elements oob of the main_grid.
                self.solved = True
        if not self.solved: #<---------------------------------------------------------------------WARNING! temp solution probably fix later.
            STEPS_COUNT += 1
            self.set_solving_current()
            if self.main_grid[self.solving_next_y][self.solving_next_x].solve():
                self.next_cell(1)
            else:
                self.next_cell(-1)
            self.refresh_grid()

    # Moves currently solved cell on demand of the step function.
    # Direction can be 1 or -1, 1 moves the cell forwards, -1 backwards.
    def next_cell(self, direction: int) -> None:
        self.solving_next_x += direction
        self.overflow_rectification()
        self.skip_unchangable(direction)

    def overflow_rectification(self) -> None: # Converts linear movement through a line into cyclic movement through a 9x9 plane.
        if self.solving_next_x > 8:
            self.solving_next_x = 0
            self.solving_next_y += 1
        elif self.solving_next_x < 0:
            self.solving_next_x = 8
            self.solving_next_y -= 1

    def skip_unchangable(self, momentum: int) -> None: # Recursively calls movement function(next_cell) if current cell is unchangable.
        if self.within_oob(self.solving_next_y): #<-------------------------------------------------------------------------WARNING! redundant oob check, revisit later
            if not self.main_grid[self.solving_next_y][self.solving_next_x].changeble:
                self.next_cell(momentum)

    def reset_solving(self) -> None: #<-------------------------------------------------------------------------WARNING! redundant revisit later
        self.solving_y = -1
        self.solving_x = -1

    def set_solving_current(self) -> None: # Stores the position of the currently solved cell in the grid.
        self.solving_y = self.solving_next_y
        self.solving_x = self.solving_next_x

    def within_oob(self, y: int = 0, x: int = 0) -> None:
        if (y >= 0 and y<= 8) and (x >= 0 and x<= 8):
            return(True)
        else:
            return(False)

    def one_step_solve(self, y: int, x: int) -> bool: # broken rn WIP
        possible_choices = [0,1,2,3,4,5,6,7,8,9]
        if x > 8: # Check oob
            x = 0 
            y += 1
        if y > 8: # Check win
            self.solved = True
            return(True) # Breakout GREATSUCCESS
        if self.main_grid[y][x].changeble:
            # Exploring choices
            for choice in possible_choices:
                # Make choice
                self.main_grid[y][x].value = choice
                # Check the choice made
                if self.main_grid[y][x].check_constraint():
                    if self.one_step_solve(y, x+1):
                        return(True) #breakout SUCCESS
                    
            self.main_grid[y][x].value = 0
            return(False) #breakout BACKTRACK

        else:
            if self.one_step_solve(y, x+1):
                return(True) #breakout SUCCESS
            else:
                return(False) #breakout BACKTRACK

class cell():
    style_not_changeble = 'QLabel {background-color: #151515; color: #bbbbbb;}' # What a mess, will change later.
    style_current_right = 'QLabel {background-color: #25aa25; color: #000000;}'
    style_current_wrong = 'QLabel {background-color: #aa2525; color: #ffffff;}'
    style_default = 'QLabel {background-color: #252525; color: #ffffff;}'
    style_next = 'QLabel {background-color: #555555; color: #ff2525;}'

    def __init__(self, y: int, x: int) -> None:
        self.value = 0                  # Value of the cell (1-9).
        self.changeble = True           # This tracks the possibility to change the value during backtrack.
        self.coord_y = y                # Coordinates of the current cell.
        self.coord_x = x
        self.label = grid_label()       # Element containing visual represetation of the current cell.
        self.last_active = 0
    
    def not_itself(self,cell:object) -> bool: # Checks if object is not self.
        if cell.coord_y == self.coord_y and cell.coord_x == self.coord_x:
            return(False)
        else:
            return(True)

    def value_check(self,cell:object) -> bool: # Checks if another cell has same value.
        if cell.value == self.value and self.not_itself(cell):
            return(True)

    # Checks if there are cells with values matching the value of the current cell.
    # in a row, column and metacell(3x3 square) containing current cell.
    def check_constraint(self) -> bool:
        if self.check_row() and self.check_column() and self.check_metacell():
            return(True)
        return(False)
    
    def check_row(self) -> bool:
        for cell in GRID.main_grid[self.coord_y]: 
            if self.value_check(cell):
                return(False)
        return(True)

    def check_column(self) -> bool:
        for row in GRID.main_grid: 
            if self.value_check(row[self.coord_x]):
                return(False)
        return(True)

    def check_metacell(self) -> bool:
        m_x = self.coord_x // 3 * 3 
        m_y = self.coord_y // 3 * 3
        for row in GRID.main_grid[m_y:m_y+2]:
            for cell in row[m_x:m_x+2]:
                if self.value_check(cell):
                    return(False)
        return(True)
   
    # Solves this specific cell.
    def solve(self) -> bool:
        self.reset_inactivity()
        while self.increment_value():
            if self.check_constraint():
               # GRID.refresh_cell(self.coord_y,self.coord_y).
                return(True)
        #GRID.refresh_cell(self.coord_y,self.coord_y).
        return(False)

    def increment_value(self) -> bool:
        self.value += 1
        if self.value > 9:
            self.value = 0
            return(False)
        else:
            return(True)

    def set_label(self) -> None: # Constructs visuals of the label.
        self.set_default()
        self.highlight_unchangeble()
        self.highlight_current()
        self.highlight_next()
        self.set_label_text()
    
    def set_default(self) -> None: # Sets a default style for all of the cells.
        self.label.setStyleSheet(self.style_default)   # Sets style for all the other cells in the window.

    def highlight_current(self) -> None: # Sets style for the active cell.
        if STEPS_COUNT > 0: # Doesnt highlight anything during the step 0.
            if not self.not_itself(GRID.main_grid[GRID.solving_y][GRID.solving_x]): # Checks if the cell is currently active.
                if self.value != 0:
                    self.label.setStyleSheet(self.style_current_right)   # Sets style for the active cell.
                else:
                    self.label.setStyleSheet(self.style_current_wrong)   # Sets style for the active cells if it is empty.
    
    def highlight_next(self) -> None: # Sets style for the cell that will be active during the next step.
        if (STEPS_COUNT > 0) and GRID.within_oob(GRID.solving_next_y, GRID.solving_next_x): # Doesnt highlight anything during the step 0 and oob.
            if not self.not_itself(GRID.main_grid[GRID.solving_next_y][GRID.solving_next_x]): # Checks if the cell will be active in the next step.
                self.label.setStyleSheet(self.style_next)   # Sets style for the next cell that will be active.

    def highlight_unchangeble(self) -> None: # Sets style for the unchangeble cells.
        if not self.changeble:
            self.label.setStyleSheet(self.style_not_changeble)   # Sets style for the unchangeble cells in the window.

    def set_label_text(self) -> None: # Assigns a string character to the associated label converted from the value of the cell.
        if self.value != 0: # If value is 0 the text field of the label ramains empty.
            self.label.setText(str(self.value))
        else:
            self.label.setText('')

    def reset_inactivity(self) -> None: # Currently unused, WIP.
        self.last_active = STEPS_COUNT

    def inactive(self) -> int: # Currently unused, WIP.
        return(STEPS_COUNT - self.last_active)

# Initializing the 9x9 grid.
GRID = gridclass()

GRID.imp_from_list(imp_grid)
GRID.refresh_grid()

window = w()
window.setCentralWidget(GRID.wid)

sys.exit(app.exec()) # End