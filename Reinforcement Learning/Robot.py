from Cell import Cell

class Robot(object):
    UP = "+0"
    DOWN = "-0"
    LEFT = "0-"
    RIGHT = "0+"

    def __init__(self, position):
        self.position = position

    def move(self, direction):
        if(direction == Robot.UP):
            print("moving up")
        elif(direction == Robot.DOWN):
            print("moving down")
        elif(direction == Robot.LEFT):
            print("moving left")
        else:
            print("moving right")

    def peek(self, grid, direction):
        if(direction == Robot.UP):
            print("peeking up")
            if(self.position[0] == 0 or grid.layout[self.position[0] - 1][self.position[1]].getType() == Cell.WALL):
                print("Out of bounds")
        elif(direction == Robot.DOWN):
            print("peeking down")
            if(self.position[0] == grid.getSize()[0] - 1 or grid.layout[self.position[0] + 1][self.position[1]].getType() == Cell.WALL):
                print("Out of bounds")
        elif(direction == Robot.LEFT):
            print("peeking left")
            if(self.position[1] == 0 or grid.layout[self.position[0]][self.position[1] - 1].getType() == Cell.WALL):
                print("Out of bounds")
        else:
            print("peeking right")
            if(self.position[1] == grid.getSize()[1] - 1 or grid.layout[self.position[0]][self.position[1] + 1].getType() == Cell.WALL):
                print("Out of bounds")