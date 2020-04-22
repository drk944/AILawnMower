import numpy as np
import msvcrt

fwd = 0
back = 1
left = 2
right = 3
diagL = 4
diagR = 5

NORTH = 0
SOUTH = 2
WEST = 3
EAST = 1


class Mower:
    def __init__(self):
        self.currScore = 0
        self.dir = NORTH
        self.returnHomeProtocol = False

    def setStartingPos(self, startingPos):
        self.TLX = startingPos[0]
        self.TLY = startingPos[1]
        self.BRX = startingPos[0] + 1
        self.BRY = startingPos[1] + 1
        self.homeTLX = self.TLX
        self.homeTLY = self.TLY
        self.homeBRX = self.BRX
        self.homeBRY = self.BRY

    def setTriangle(self, startingPos):
        self.P1X = startingPos[0]
        self.P1Y = startingPos[1] + 1
        self.P2X = startingPos[0] + 1
        self.P2Y = startingPos[1]
        self.P3X = startingPos[0]
        self.P3Y = startingPos[1] - 1

    def updateTriangle(self):
        self.P1X = self.TLX
        self.P1Y = self.TLY + 1
        self.P2X = self.TLX + 1
        self.P2Y = self.TLY
        self.P3X = self.TLX
        self.P3Y = self.TLY - 1

    def drawTriangle(self):
        if self.dir == NORTH:
            self.P1X = self.TLX
            self.P1Y = self.TLY + 1

            self.P2X = self.TLX + 1
            self.P2Y = self.TLY

            self.P3X = self.TLX
            self.P3Y = self.TLY - 1

        if self.dir == SOUTH:
            self.P1X = self.TLX
            self.P1Y = self.TLY + 1

            self.P2X = self.TLX + 1
            self.P2Y = self.TLY

            self.P3X = self.BRX - 1
            self.P3Y = self.BRY

        if self.dir == EAST:
            self.P1X = self.TLX + 1
            self.P1Y = self.TLY

            self.P2X = self.TLX
            self.P2Y = self.TLY + 1

            self.P3X = self.BRX
            self.P3Y = self.BRY - 1

        if self.dir == WEST:
            self.P1X = self.TLX + 1
            self.P1Y = self.TLY

            self.P2X = self.TLX
            self.P2Y = self.TLY + 1

            self.P3X = self.TLX - 1
            self.P3Y = self.TLY

    def makeMove(self, lawn):
        moves = {
            'w': 0,
            's': 2,
            'a': 3,
            'd': 1,
        }
        oldPositions = self.getPosition()
        oldOrientation = self.dir

        move = self.getNextMove(lawn)
        # -1 is the default value if there is no keys that matches the input
        # print('The result for inp is : ', userIn.get(userInput, -1))

        if move == 0:
            self.fwd_move()
        if move == 2:
            self.bwd_move()
        if move == 3:
            self.l_move()
        if move == 1:
            self.r_move()

        # if userInput == diagL:
        #
        # if userInput == diagR:

        if self.isValidMove(lawn):
            pass
        else:
            self.dir = oldOrientation
            self.TLX = oldPositions[0]
            self.TLY = oldPositions[1]
            self.BRX = oldPositions[2]
            self.BRY = oldPositions[3]
            self.drawTriangle()

    def getNextMove(self, lawn):
        if self.returnHomeProtocol:
            startingPlace = [[self.TLY, self.TLX]]
            potentialPaths = [999, 999, 999, 999]
            # pDir = self.getNeighbors(lawn, self.TLX, self.TLY)
            neighbors = self.getNeighbors(lawn, self.TLX, self.TLY)
            pDir = []
            for i in neighbors:
                if lawn[i[1]][i[0]] == 4:
                    pDir.append(i)
            if len(pDir) == 0:
                pDir = neighbors

            for i in range(len(pDir)):  # pDir -> potential Directions
                validPath, pathCost = self.generatePathHome(lawn, pDir[i][1], pDir[i][0], startingPlace, 0, 4)
                if validPath:
                    potentialPaths[i] = pathCost
            bd = np.where(potentialPaths == np.amin(potentialPaths))
            directionToGo = 0
            for i in range(4):
                if potentialPaths[i] == np.amin(potentialPaths):
                    directionToGo = i
            posX = pDir[directionToGo][1]
            posY = pDir[directionToGo][0]

            if posX > self.TLX:
                bdInt = 1
            elif posX < self.TLX:
                bdInt = 3
            elif posY < self.TLY:
                bdInt = 0
            elif posY > self.TLY:
                bdInt = 2

        else:
            # Mowing
            # attempting a greedy algorithm
            possibleMoves = self.findAvailableMoves(lawn)

            bd = np.where(possibleMoves == np.amax(possibleMoves))  # bd = bestDirection
            max = np.amax(possibleMoves)
            for i in range(4):
                if possibleMoves[i] == np.amax(possibleMoves):
                    bdInt = i
            if possibleMoves[bdInt] == 0:
                #  our greedy algorithm has failed, time to seek and destroy!
                bdInt = self.seekAndDestroy(lawn)

        # now to line up the orientation of the mower
        if self.dir == bdInt:
            return 0  # if the direction we want to go lines up with the mower orientation, go forward
        if (self.dir + 1 % 4) == bdInt:
            return 1  # if we need to increment by one, that means turn right
        if (self.dir + 3) % 4 == bdInt:
            return 3
        if (self.dir + 2) % 4 == bdInt:     # recently added to cope with seek and destroy
            return 1
        # if all else has failed, just go to the right/ spin right
        return 1  # defualt, spin right

    def seekAndDestroy(self, lawn):
        # first step, find where we missed
        rows = lawn.shape[0]
        cols = lawn.shape[1]
        grassFound = False
        for x in range(0, rows):
            for y in range(0, cols):
                if lawn[x, y] == 2:
                    grassFound = True
                    break
            if grassFound:
                break
        if grassFound:
            startingPlace = [[self.TLY, self.TLX]]
            potentialPaths = [999, 999, 999, 999]
            # pDir = self.getNeighbors(lawn, self.TLX, self.TLY)
            neighbors = self.getNeighbors(lawn, self.TLX, self.TLY)
            pDir = []
            for i in neighbors:
                if lawn[i[1]][i[0]] == 2:
                    pDir.append(i)
            if len(pDir) == 0:
                pDir = neighbors

            for i in range(len(pDir)):  # pDir -> potential Directions
                validPath, pathCost = self.generatePathHome(lawn, pDir[i][1], pDir[i][0], startingPlace, 0, 2)
                if validPath:
                    potentialPaths[i] = pathCost
            bd = np.where(potentialPaths == np.amin(potentialPaths))
            directionToGo = 0
            for i in range(4):
                if potentialPaths[i] == np.amin(potentialPaths):
                    directionToGo = i
            posX = pDir[directionToGo][1]
            posY = pDir[directionToGo][0]

            if posX > self.TLX:
                bdInt = 1
            elif posX < self.TLX:
                bdInt = 3
            elif posY < self.TLY:
                bdInt = 0
            elif posY > self.TLY:
                bdInt = 2
            return bdInt
        else:
            return 0

    def generatePathHome(self, lawn, xPos, yPos, visited, numSteps, whatWereLooking4):
        # Terminate if the goal is reached
        # if xPos == self.homeTLX and yPos == self.homeTLY and xPos + 1 == self.homeBRX and yPos + 1 == self.homeBRY:
        if lawn[yPos][xPos] == whatWereLooking4 and lawn[yPos + 1][xPos + 1] == whatWereLooking4:
            return True, numSteps
        if numSteps >= 100:
            return False, 5

        visited.append([yPos, xPos])
        # numSteps = numSteps + 1
        neighbors = self.getNeighbors(lawn, xPos, yPos)
        for i in neighbors:
            if visited.__contains__(i):
                neighbors.remove(i)
        preferredNeighbors = []
        for i in neighbors:
            if lawn[i[1]][i[0]] == whatWereLooking4:
                preferredNeighbors.append(i)
        if len(preferredNeighbors) == 0:
            preferredNeighbors = neighbors

        for i in preferredNeighbors:
            success, numSteps = self.generatePathHome(lawn, i[1], i[0], visited, numSteps + 1, whatWereLooking4)
            if success:
                return True, numSteps

        return False, numSteps

    def getNeighbors(self, lawn, xPos, yPos):
        neighbors = []
        if xPos >= 1:
            if (lawn[yPos][xPos - 1] == 1 or lawn[yPos][xPos - 1] == 4 or lawn[yPos][xPos - 1] == 2) and \
                    (lawn[yPos + 1][xPos - 1] == 1 or lawn[yPos + 1][xPos - 1] == 4 or lawn[yPos + 1][xPos - 1] == 2):  # to the left
                neighbors.append([yPos, xPos - 1])
        if xPos < lawn.shape[0] - 1:  # - 1 to accommodate the full size of the mower
            if (lawn[yPos][xPos + 2] == 1 or lawn[yPos][xPos + 2] == 4 or lawn[yPos][xPos + 2] == 2) and \
                    (lawn[yPos + 1][xPos + 2] == 1 or lawn[yPos + 1][xPos + 2] == 4 or lawn[yPos + 1][xPos + 2] == 2):  # to the Right
                neighbors.append([yPos, xPos + 1])
        if yPos < lawn.shape[1] - 1:  # - 1 to accommodate the full size of the mower
            if (lawn[yPos + 2][xPos] == 1 or lawn[yPos + 2][xPos] == 4 or lawn[yPos + 2][xPos] == 2) and \
                    (lawn[yPos + 2][xPos + 1] == 1 or lawn[yPos + 2][xPos + 1] == 4 or lawn[yPos + 2][xPos + 1] == 2):  # or lawn[yPos + 1][xPos] == 4:  # below
                neighbors.append([yPos + 1, xPos])
        if yPos >= 1:
            if (lawn[yPos - 1][xPos] == 1 or lawn[yPos - 1][xPos] == 4 or lawn[yPos - 1][xPos] == 2) and \
                    (lawn[yPos - 1][xPos + 1] == 1 or lawn[yPos - 1][xPos + 1] == 4 or lawn[yPos - 1][xPos + 1] == 2):  # above
                neighbors.append([yPos - 1, xPos])
        return neighbors

    def findAvailableMoves(self, lawn):
        movesList = np.array([0, 0, 0, 0])  # [up, right, down, left] i.e. clockwise of eachother
        # note, these directions are not in relation to the orientation of the mower
        # check above
        if self.TLY >= 1:
            totalVals = 0
            if lawn[self.TLY - 1][self.TLX] == 2 and (lawn[self.TLY-1][self.BRX] == 1 or lawn[self.TLY-1][self.BRX] == 2):
                totalVals = totalVals + 2
            if lawn[self.TLY - 1][self.BRX] == 2 and (lawn[self.TLY-1][self.TLX] == 1 or lawn[self.TLY-1][self.TLX] == 2):
                totalVals = totalVals + 2
            movesList[0] = totalVals

        # checking Right
        if self.BRX <= lawn.shape[0] - 1:
            totalVals = 0
            if lawn[self.TLY][self.BRX + 1] == 2 and (lawn[self.BRY][self.BRX + 1] == 2 or lawn[self.BRY][self.BRX + 1] == 1):
                totalVals = totalVals + 2
            if lawn[self.BRY][self.BRX + 1] == 2 and (lawn[self.TLY][self.BRX + 1] == 2 or lawn[self.TLY][self.BRX + 1] == 1):
                totalVals = totalVals + 2
            movesList[1] = totalVals

        # checking down
        if self.BRY <= lawn.shape[1] - 1:
            totalVals = 0
            if lawn[self.BRY + 1][self.TLX] == 2 and (lawn[self.BRY + 1][self.BRX] == 2 or lawn[self.BRY + 1][self.BRX] == 1):
                totalVals = totalVals + 2
            if lawn[self.BRY + 1][self.BRX] == 2 and (lawn[self.BRY + 1][self.TLX] == 2 or lawn[self.BRY + 1][self.TLX] == 1):
                totalVals = totalVals + 2
            movesList[2] = totalVals

        # checking Left
        if self.TLX >= 1:
            totalVals = 0
            if lawn[self.TLY][self.TLX - 1] == 2 and (lawn[self.BRY][self.TLX - 1] == 2 or lawn[self.BRY][self.TLX - 1] == 1):
                totalVals = totalVals + 2
            if lawn[self.BRY][self.TLX - 1] == 2 and (lawn[self.TLY][self.TLX - 1] == 2 or lawn[self.TLY][self.TLX - 1] == 1):
                totalVals = totalVals + 2
            movesList[3] = totalVals

        return movesList

    def isDone(self, lawn):
        if 2 in lawn:
            return False
        if not self.isMowerHome():
            self.returnHomeProtocol = True
            return False
        else:
            return True

    def fwd_move(self):
        if self.dir == NORTH:
            self.TLY = self.TLY - 1
            self.BRY = self.BRY - 1
            # self.updateTriangle()
        if self.dir == SOUTH:
            self.TLY = self.TLY + 1
            self.BRY = self.BRY + 1
            # self.updateTriangle()
        if self.dir == EAST:
            self.TLX = self.TLX + 1
            self.BRX = self.BRX + 1
        if self.dir == WEST:
            self.TLX = self.TLX - 1
            self.BRX = self.BRX - 1
        self.drawTriangle()

    def bwd_move(self):
        if self.dir == SOUTH:
            self.TLY = self.TLY - 1
            self.BRY = self.BRY - 1
        if self.dir == NORTH:
            self.TLY = self.TLY + 1
            self.BRY = self.BRY + 1
        if self.dir == WEST:
            self.TLX = self.TLX + 1
            self.BRX = self.BRX + 1
        if self.dir == EAST:
            self.TLX = self.TLX - 1
            self.BRX = self.BRX - 1
        self.drawTriangle()

    def r_move(self):
        if self.dir == NORTH:
            self.dir = EAST
        elif self.dir == SOUTH:
            self.dir = WEST
        elif self.dir == EAST:
            self.dir = SOUTH
        elif self.dir == WEST:
            self.dir = NORTH
        self.drawTriangle()

    def l_move(self):
        if self.dir == NORTH:
            self.dir = WEST
        elif self.dir == SOUTH:
            self.dir = EAST
        elif self.dir == EAST:
            self.dir = NORTH
        elif self.dir == WEST:
            self.dir = SOUTH
        self.drawTriangle()

    def getPosition(self):
        return self.TLX, self.TLY, self.BRX, self.BRY

    def getTriangle(self):
        return self.P1X, self.P1Y, self.P2X, self.P2Y, self.P3X, self.P3Y

    # def mow(self, lawn):

    def isMowerHome(self):
        if self.TLX == self.homeTLX and self.TLY == self.homeTLY and self.BRX == self.homeBRX and self.BRY == self.homeBRY:
            return True
        else:
            return False

    def isValidMove(self, lawn):
        mowed = self.getPosition()
        if ((lawn[mowed[1]][mowed[0]] == 1 or lawn[mowed[1]][mowed[0]] == 2 or lawn[mowed[1]][mowed[0]] == 4) and
                (lawn[mowed[1]][mowed[0] + 1] == 1 or lawn[mowed[1]][mowed[0] + 1] == 2 or lawn[mowed[1]][
                    mowed[0] + 1] == 4) and
                (lawn[mowed[3]][mowed[2]] == 1 or lawn[mowed[3]][mowed[2]] == 2 or lawn[mowed[3]][mowed[2]] == 4) and
                (lawn[mowed[3]][mowed[2] - 1] == 1 or lawn[mowed[3]][mowed[2] - 1] == 2 or lawn[mowed[3]][
                    mowed[2] - 1] == 4)):
            return True
        else:
            return False

    def updateLawn(self, lawn):
        # return self.TLX, self.TLY, self.BRX, self.BRY
        if self.isNotAHomePosition(self.TLX, self.TLY):
            lawn[self.TLY][self.TLX] = 1
        if self.isNotAHomePosition(self.BRX, self.TLY):
            lawn[self.TLY][self.BRX] = 1
        if self.isNotAHomePosition(self.TLX, self.BRY):
            lawn[self.BRY][self.TLX] = 1
        if self.isNotAHomePosition(self.BRX, self.BRY):
            lawn[self.BRY][self.BRX] = 1

            # lawn[mowed[1]][mowed[0]] = 1
        # lawn[mowed[1]][mowed[0] + 1] = 1
        # lawn[mowed[3]][mowed[2]] = 1
        # lawn[mowed[3]][mowed[2] - 1] = 1
        return lawn

    def isNotAHomePosition(self, pos1, pos2):
        if (pos1 == self.homeTLX and pos2 == self.homeTLY) or (pos1 == self.homeBRX and pos2 == self.homeTLY) or \
                (pos1 == self.homeTLX and pos2 == self.homeBRY) or (pos1 == self.homeBRX and pos2 == self.homeBRY):
            return False
        else:
            return True


class Mower_User:
    def __init__(self):
        self.currScore = 0
        self.dir = NORTH

    def setStartingPos(self, startingPos):
        self.TLX = startingPos[0]
        self.TLY = startingPos[1]
        self.BRX = startingPos[0] + 1
        self.BRY = startingPos[1] + 1
        self.homeTLX = self.TLX
        self.homeTLY = self.TLY
        self.homeBRX = self.BRX
        self.homeBRY = self.BRY

    def setTriangle(self, startingPos):
        self.P1X = startingPos[0]
        self.P1Y = startingPos[1] + 1
        self.P2X = startingPos[0] + 1
        self.P2Y = startingPos[1]
        self.P3X = startingPos[0]
        self.P3Y = startingPos[1] - 1

    def updateTriangle(self):
        self.P1X = self.TLX
        self.P1Y = self.TLY + 1
        self.P2X = self.TLX + 1
        self.P2Y = self.TLY
        self.P3X = self.TLX
        self.P3Y = self.TLY - 1

    def drawTriangle(self):
        if self.dir == NORTH:
            self.P1X = self.TLX
            self.P1Y = self.TLY + 1

            self.P2X = self.TLX + 1
            self.P2Y = self.TLY

            self.P3X = self.TLX
            self.P3Y = self.TLY - 1

        if self.dir == SOUTH:
            self.P1X = self.TLX
            self.P1Y = self.TLY + 1

            self.P2X = self.TLX + 1
            self.P2Y = self.TLY

            self.P3X = self.BRX - 1
            self.P3Y = self.BRY

        if self.dir == EAST:
            self.P1X = self.TLX + 1
            self.P1Y = self.TLY

            self.P2X = self.TLX
            self.P2Y = self.TLY + 1

            self.P3X = self.BRX
            self.P3Y = self.BRY - 1

        if self.dir == WEST:
            self.P1X = self.TLX + 1
            self.P1Y = self.TLY

            self.P2X = self.TLX
            self.P2Y = self.TLY + 1

            self.P3X = self.TLX - 1
            self.P3Y = self.TLY

    def makeMove(self, lawn):
        userIn = {
            'w': 0,
            's': 1,
            'a': 2,
            'd': 3,
            'q': 4,
            'r': 5
        }
        # take user input
        # userInput = msvcrt.getch()

        oldPositions = self.getPosition()
        oldOrientation = self.dir
        # return self.TLX, self.TLY, self.BRX, self.BRY

        userInput = input("Pick a direction ")
        # -1 is the default value if there is no keys that matches the input
        # print('The result for inp is : ', userIn.get(userInput, -1))

        if userInput == "w":
            self.fwd_move(lawn)
        if userInput == "s":
            self.bwd_move(lawn)
        if userInput == "a":
            self.l_move()
        if userInput == "d":
            self.r_move(lawn)

        # if userInput == diagL:
        #
        # if userInput == diagR:

        if self.isValidMove(lawn):
            pass
        else:
            self.dir = oldOrientation
            self.TLX = oldPositions[0]
            self.TLY = oldPositions[1]
            self.BRX = oldPositions[2]
            self.BRY = oldPositions[3]
            self.drawTriangle()

    def fwd_move(self, lawn):
        if self.dir == NORTH:
            self.TLY = self.TLY - 1
            self.BRY = self.BRY - 1
            # self.updateTriangle()
        if self.dir == SOUTH:
            self.TLY = self.TLY + 1
            self.BRY = self.BRY + 1
            # self.updateTriangle()
        if self.dir == EAST:
            self.TLX = self.TLX + 1
            self.BRX = self.BRX + 1
        if self.dir == WEST:
            self.TLX = self.TLX - 1
            self.BRX = self.BRX - 1
        self.drawTriangle()

    def bwd_move(self, lawn):
        if self.dir == SOUTH:
            self.TLY = self.TLY - 1
            self.BRY = self.BRY - 1
        if self.dir == NORTH:
            self.TLY = self.TLY + 1
            self.BRY = self.BRY + 1
        if self.dir == WEST:
            self.TLX = self.TLX + 1
            self.BRX = self.BRX + 1
        if self.dir == EAST:
            self.TLX = self.TLX - 1
            self.BRX = self.BRX - 1
        self.drawTriangle()

    def r_move(self, lawn):
        if self.dir == NORTH:
            self.dir = EAST
        elif self.dir == SOUTH:
            self.dir = WEST
        elif self.dir == EAST:
            self.dir = SOUTH
        elif self.dir == WEST:
            self.dir = NORTH
        self.drawTriangle()

    def l_move(self):
        if self.dir == NORTH:
            self.dir = WEST
        elif self.dir == SOUTH:
            self.dir = EAST
        elif self.dir == EAST:
            self.dir = NORTH
        elif self.dir == WEST:
            self.dir = SOUTH
        self.drawTriangle()

    def getPosition(self):
        return self.TLX, self.TLY, self.BRX, self.BRY

    def getTriangle(self):
        return self.P1X, self.P1Y, self.P2X, self.P2Y, self.P3X, self.P3Y

    # def mow(self, lawn):

    def isMowerHome(self):
        if self.TLX == self.homeTLX and self.TLY == self.homeTLY and self.BRX == self.homeBRX and self.BRY == self.homeBRY:
            return True
        else:
            return False

    def isValidMove(self, lawn):
        mowed = self.getPosition()
        if ((lawn[mowed[1]][mowed[0]] == 1 or lawn[mowed[1]][mowed[0]] == 2 or lawn[mowed[1]][mowed[0]] == 4) and
                (lawn[mowed[1]][mowed[0] + 1] == 1 or lawn[mowed[1]][mowed[0] + 1] == 2 or lawn[mowed[1]][
                    mowed[0] + 1] == 4) and
                (lawn[mowed[3]][mowed[2]] == 1 or lawn[mowed[3]][mowed[2]] == 2 or lawn[mowed[3]][mowed[2]] == 4) and
                (lawn[mowed[3]][mowed[2] - 1] == 1 or lawn[mowed[3]][mowed[2] - 1] == 2 or lawn[mowed[3]][
                    mowed[2] - 1] == 4)):
            return True
        else:
            return False

    def updateLawn(self, lawn):
        # return self.TLX, self.TLY, self.BRX, self.BRY
        if self.isNotAHomePosition(self.TLX, self.TLY):
            lawn[self.TLY][self.TLX] = 1
        if self.isNotAHomePosition(self.BRX, self.TLY):
            lawn[self.TLY][self.BRX] = 1
        if self.isNotAHomePosition(self.TLX, self.BRY):
            lawn[self.BRY][self.TLX] = 1
        if self.isNotAHomePosition(self.BRX, self.BRY):
            lawn[self.BRY][self.BRX] = 1
        return lawn

    def isNotAHomePosition(self, pos1, pos2):
        if (pos1 == self.homeTLX and pos2 == self.homeTLY) or (pos1 == self.homeBRX and pos2 == self.homeTLY) or \
                (pos1 == self.homeTLX and pos2 == self.homeBRY) or (pos1 == self.homeBRX and pos2 == self.homeBRY):
            return False
        else:
            return True

    def isDone(self, lawn):
        if 2 in lawn:
            return False
        if not self.isMowerHome():
            return False
        else:
            return True
