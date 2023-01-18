from Cell import Cell

class Controller(object):
    def __init__(self, grid, position):
        self.grid = grid
        self.setTarget(position)

    def setTarget(self, targetPosition):
        self.grid.setCell(targetPosition[0], targetPosition[1], Cell.TARGET)