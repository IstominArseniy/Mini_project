from libConnector import*
from ModelClass import Model
from matplotlib import pyplot as plt
import numpy as np

def main():
    zeroPointCoord = []
    # model = read_msh_file("cube_low.msh")
    model = Model("cube.msh", k=0.12, b=0.01, m=1, dt=0.3)
    model.stretch('y', 1.2)
    makeVTKSnapshot(model, 0)
    N = 300
    for i in range(1, N):
        if i % 10 == 0:
            print("Step "+ str(i) + " out of " + str(N))
        # print(model.nodeVelocities)
        model.calculateAccelerations()
        model.update()
        makeVTKSnapshot(model, i)
        zeroPointCoord.append(model.getPointCoord(0)[1])
    # print(zeroPointCoord)
    l = len(zeroPointCoord)
    plt.scatter(np.arange(0, l * 0.3, 0.3), zeroPointCoord, color='b')
    # plt.scatter(np.arange(0, l * 0.3, 0.3), 5 * np.sin((model.k / model.m) ** 0.5 * np.arange(0, l * 0.3, 0.3)), color='r')
    plt.savefig("y(t)_high.png")
    plt.show()


main()