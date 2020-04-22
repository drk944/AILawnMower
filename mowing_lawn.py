import argparse
from tkinter import *
import time
import numpy as np

from mower import Mower_User
from mower import Mower

tk = Tk()
canvas = Canvas(tk, width=500, height=400)
MAX_WIDTH = 20
MAX_HEIGHT = 30
homeTL = [-1, -1]
mowerUser = Mower()    # Change this to switch between user and AI
CORNER_OFFSET = 5
tl_x = CORNER_OFFSET
tl_y = CORNER_OFFSET
SQUARE_W = 20

mowedColor = '#%02x%02x%02x' % (41, 138, 10)
initColor = '#%02x%02x%02x' % (48, 220, 0)

fwd = 0
back = 1
left = 2
right = 3
diagL = 4
diagR = 5

def setup(mowerNum):
    initlawn = np.zeros([MAX_HEIGHT * 2, MAX_WIDTH * 2])
    tk.configure(background='green')

    tk.title("Yard")
    canvas.pack()
    canvas.config(bg="black")

    column = 0
    row = 0
    HOME_LOCATION_VAL = 4
    TREE = 5
    UNKNOWN_OBSTACLE = 6
    with open("yard_map.txt") as yard_obj:
        for line in yard_obj:
            for ch in line:
                markerVal = 0
                if ch == '-':
                    markerVal = 2
                if ch == 'x':  # number value to represent home location
                    markerVal = HOME_LOCATION_VAL
                if ch == 'T' or ch == 't':  # number value to represent home location
                    markerVal = TREE
                for i in range(2):
                    for j in range(2):
                        initlawn[row + i][column + j] = markerVal
                column += 2
            row += 2
            column = 0

    # Draw the initial lawn
    homeTL = [-1, -1]
    for ix, iy in np.ndindex(initlawn.shape):
        if initlawn[ix][iy] == 2:
            canvas.create_rectangle((iy * SQUARE_W + CORNER_OFFSET), (ix * SQUARE_W + CORNER_OFFSET),
                                    (iy * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                    (ix * SQUARE_W + CORNER_OFFSET + SQUARE_W), fill=initColor)
        if initlawn[ix][iy] == HOME_LOCATION_VAL:
            canvas.create_rectangle((iy * SQUARE_W + CORNER_OFFSET), (ix * SQUARE_W + CORNER_OFFSET),
                                    (iy * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                    (ix * SQUARE_W + CORNER_OFFSET + SQUARE_W), fill="white")
            if homeTL[0] == -1:
                homeTL = [iy, ix]
                mowerUser.setStartingPos(homeTL)
                mowerUser.setTriangle(homeTL)

        if initlawn[ix][iy] == TREE:
            canvas.create_rectangle((iy * SQUARE_W + CORNER_OFFSET), (ix * SQUARE_W + CORNER_OFFSET),
                                    (iy * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                    (ix * SQUARE_W + CORNER_OFFSET + SQUARE_W), fill="brown")
    print(initlawn)
    return initlawn


def main(mowerNum):
    lawn = setup(mowerNum)
    if mowerNum == 0:
        mower = Mower()
    else:
        mower = mowerUser

    # # draw the initial mower location
    mowerID = canvas.create_rectangle((mower.getPosition()[0] * SQUARE_W + CORNER_OFFSET),
                                      (mower.getPosition()[1] * SQUARE_W + CORNER_OFFSET),
                                      (mower.getPosition()[2] * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                      (mower.getPosition()[3] * SQUARE_W + CORNER_OFFSET + SQUARE_W), fill="red")
    mowerTriID = canvas.create_polygon((mower.getTriangle()[0] * SQUARE_W + CORNER_OFFSET),
                                       (mower.getTriangle()[1] * SQUARE_W + CORNER_OFFSET),
                                       (mower.getTriangle()[2] * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                       (mower.getTriangle()[3] * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                       (mower.getTriangle()[4] * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                       (mower.getTriangle()[5] * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                       outline='black',
                                       fill='black', width=0)
    # drawMower(mower)
    # tk0.mainloop()
    lawn = mower.updateLawn(lawn)
    while not mower.isDone(lawn):
    # while 2 in lawn[:, :]:
        tk.update_idletasks()
        tk.update()
        # do stuff
        canvas.delete(mowerID)
        canvas.delete(mowerTriID)

        lawn = mower.updateLawn(lawn)
        mower.makeMove(lawn)

        # update lawn:
        for ix, iy in np.ndindex(lawn.shape):
            if lawn[ix][iy] == 2:
                canvas.create_rectangle((iy * SQUARE_W + CORNER_OFFSET), (ix * SQUARE_W + CORNER_OFFSET),
                                        (iy * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                        (ix * SQUARE_W + CORNER_OFFSET + SQUARE_W), fill=initColor)
            if lawn[ix][iy] == 4:
                canvas.create_rectangle((iy * SQUARE_W + CORNER_OFFSET), (ix * SQUARE_W + CORNER_OFFSET),
                                        (iy * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                        (ix * SQUARE_W + CORNER_OFFSET + SQUARE_W), fill="white")

            if lawn[ix][iy] == 1:
                canvas.create_rectangle((iy * SQUARE_W + CORNER_OFFSET), (ix * SQUARE_W + CORNER_OFFSET),
                                        (iy * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                        (ix * SQUARE_W + CORNER_OFFSET + SQUARE_W), fill=mowedColor)


        mowerID = canvas.create_rectangle((mower.getPosition()[0] * SQUARE_W + CORNER_OFFSET),
                                          (mower.getPosition()[1] * SQUARE_W + CORNER_OFFSET),
                                          (mower.getPosition()[2] * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                          (mower.getPosition()[3] * SQUARE_W + CORNER_OFFSET + SQUARE_W), fill="red")
        mowerTriID = canvas.create_polygon((mower.getTriangle()[0] * SQUARE_W + CORNER_OFFSET),
                                           (mower.getTriangle()[1] * SQUARE_W + CORNER_OFFSET),
                                           (mower.getTriangle()[2] * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                           (mower.getTriangle()[3] * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                           (mower.getTriangle()[4] * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                           (mower.getTriangle()[5] * SQUARE_W + CORNER_OFFSET + SQUARE_W),
                                           outline='black',
                                           fill='black', width=0)
        # time.sleep(0.5)

if __name__ == "__main__":
    main(1)
