from Controller import Controller
from Grid import Grid
from Robot import Robot

grid = Grid()
target = [6, 3]
controller = Controller(grid, target)

robot1 = Robot(grid, [2, 1])
robot2 = Robot(grid, [5, 6])

grid.printGrid()

robot1.move(Robot.RIGHT)
robot2.move(Robot.DOWN)

grid.printGrid()

print(robot2.peek(Robot.LEFT))