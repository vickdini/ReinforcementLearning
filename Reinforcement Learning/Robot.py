from Cell import Cell

class Robot(object):
    UP = "-0"
    DOWN = "+0"
    LEFT = "0-"
    RIGHT = "0+"

    def __init__(self, position):
        self.position = position

    # This function effectively moves a robot, if possible, after "peeking" to check if moving to the destination cell is possible
    def move(self, grid, direction):
        if(direction == Robot.UP):
            if(self.peek(grid, direction) >= 0):
                grid.setCell(self.position[0], self.position[1], Cell.EMPTY)
                grid.setCell(self.position[0] - 1, self.position[1], Cell.ROBOT)
        elif(direction == Robot.DOWN):
            if(self.peek(grid, direction) >= 0):
                grid.setCell(self.position[0], self.position[1], Cell.EMPTY)
                grid.setCell(self.position[0] + 1, self.position[1], Cell.ROBOT)
        elif(direction == Robot.LEFT):
            if(self.peek(grid, direction) >= 0):
                grid.setCell(self.position[0], self.position[1], Cell.EMPTY)
                grid.setCell(self.position[0], self.position[1] - 1, Cell.ROBOT)
        else:
            if(self.peek(grid, direction) >= 0):
                grid.setCell(self.position[0], self.position[1], Cell.EMPTY)
                grid.setCell(self.position[0], self.position[1] + 1, Cell.ROBOT)
    
    # With this function a robot may take a "peek" at the adjacent cell in a specific direction to check if it exists (in case of grid boundaries),
    # if there's a wall, another robot, or if it's empty.
    # It returns -1 if the intended move is impossible
    # 0 if it's an empty cell
    # 1 if there's another robot in the destination cell
    def peek(self, grid, direction):
        if(direction == Robot.UP):
            print("peeking up")
            if(self.position[0] == 0 or grid.layout[self.position[0] - 1][self.position[1]].getType() == Cell.WALL):
                return -1
            elif(grid.layout[self.position[0] - 1][self.position[1]].getType() == Cell.ROBOT):
                return 1
            else:
                return 0
        elif(direction == Robot.DOWN):
            print("peeking down")
            if(self.position[0] == grid.getSize()[0] - 1 or grid.layout[self.position[0] + 1][self.position[1]].getType() == Cell.WALL):
                return -1
            elif(grid.layout[self.position[0] + 1][self.position[1]].getType() == Cell.ROBOT):
                return 1
            else:
                return 0
        elif(direction == Robot.LEFT):
            print("peeking left")
            if(self.position[1] == 0 or grid.layout[self.position[0]][self.position[1] - 1].getType() == Cell.WALL):
                return -1
            elif(grid.layout[self.position[0]][self.position[1] - 1].getType() == Cell.ROBOT):
                return 1
            else:
                return 0
        else:
            print("peeking right")
            if(self.position[1] == grid.getSize()[1] - 1 or grid.layout[self.position[0]][self.position[1] + 1].getType() == Cell.WALL):
                return -1
            elif(grid.layout[self.position[0]][self.position[1] + 1].getType() == Cell.ROBOT):
                return 1
            else:
                return 0