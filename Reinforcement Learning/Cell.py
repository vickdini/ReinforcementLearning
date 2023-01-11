class Cell(object):
    EMPTY = "  "
    WALL = "██"
    ROBOT = "RR"

    def __init__(self, type):
        self.type = type

    def getChar(self):
        return self.type