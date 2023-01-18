from Cell import Cell

class Grid(object):
    def __init__(self):
        self.layout = [
            [Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY)],
            [Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.WALL), Cell(Cell.WALL), Cell(Cell.WALL), Cell(Cell.WALL), Cell(Cell.WALL)],
            [Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.WALL), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY)],
            [Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.WALL), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY)],
            [Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.WALL), Cell(Cell.EMPTY), Cell(Cell.WALL), Cell(Cell.EMPTY), Cell(Cell.EMPTY)],
            [Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.WALL), Cell(Cell.EMPTY), Cell(Cell.EMPTY)],
            [Cell(Cell.WALL), Cell(Cell.WALL), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.WALL), Cell(Cell.EMPTY), Cell(Cell.EMPTY)],
            [Cell(Cell.WALL), Cell(Cell.WALL), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.EMPTY), Cell(Cell.WALL), Cell(Cell.EMPTY), Cell(Cell.EMPTY)]
            ]

    def getSize(self):
        return [len(self.layout), len(self.layout[0])]

    def setCell(self, row, column, cellType):
        self.layout[row][column] = Cell(cellType)

    def printGrid(self):
        print()

        for i in range(len(self.layout)):
            print(Cell.WALL, end = "")
        print(Cell.WALL + Cell.WALL)

        for row in self.layout:
            print(Cell.WALL, end = "")
            for cell in row:
                print(cell.getType(), end = "")
            print(Cell.WALL)
        
        for i in range(len(self.layout)):
            print(Cell.WALL, end = "")
        print(Cell.WALL + Cell.WALL)
        print()