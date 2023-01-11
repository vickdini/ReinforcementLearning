from Cell import Cell
from Controller import Controller
from Grid import Grid
from Robot import Robot

grid = Grid()
b = Controller()
c = Robot([2, 1])

d = Cell(Cell.EMPTY)

grid.printGrid()

c.move(Robot.UP)
c.peek(grid, Robot.DOWN)

print(grid.getSize()[0] - 1)