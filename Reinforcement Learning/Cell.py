class Cell(object):
    EMPTY = "  "
    WALL = "██"
    ROBOT = "RR"

    def __init__(self, type):
        self.type = type

    def getType(self):
        return self.type