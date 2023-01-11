from Cell import Cell
from Controller import Controller
from Grid import Grid
from Robot import Robot

grid = Grid()
b = Controller()
robot1 = Robot([2, 1])
robot2 = Robot([5, 6])

d = Cell(Cell.EMPTY)

grid.printGrid()

robot1.move(grid, Robot.RIGHT)
robot2.move(grid, Robot.DOWN)

grid.printGrid()

print(robot2.peek(grid, Robot.LEFT))