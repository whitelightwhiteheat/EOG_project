from random import randint

Calibrating = 1
Mid = 2
Right = 3
Down = 4
Left = 5
Up = 6
NC = 7
U2 = 8
D2 = 9
L2 = 10
R2 = 11

def getRndState():
    return randint(1,6)
def printState(state):
    if state == 1:
        print("Calibrating")
    elif state == 2:
        print("Mid")
    elif state == 3:
        print("Right")
    elif state == 4:
        print("Down")
    elif state == 5:
        print("Left")
    elif state == 6:
        print("Up")
    elif state == 7:
        print("NC")
    elif state == 8:
        print("U2")
    elif state == 9:
        print("D2")
    elif state == 10:
        print("L2")
    elif state == 11:
        print("R2")