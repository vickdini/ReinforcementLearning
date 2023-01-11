class Robot(object):
    UP = "+0"
    DOWN = "-0"
    LEFT = "0-"
    RIGHT = "0+"

    def __init__(self):
        print("Inside the robot")
        position = [3, 2]

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
            if(self.position[0] == 0):
                print("Out of bounds")
            print("peeking up")
        elif(direction == Robot.DOWN):
            if(self.position[0] == grid.getSize()[0] - 1):
                print("Out of bounds")
            print("peeking down")
        elif(direction == Robot.LEFT):
            print("peeking left")
            if(self.position[1] == 0):
                print("Out of bounds")
        else:
            print("peeking right")
            if(self.position[1] == grid.getSize()[1] - 1):
                print("Out of bounds")