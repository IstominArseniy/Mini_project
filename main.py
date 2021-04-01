from libConnector import*
from MeshClass import Mesh


def main():
    model = read_msh_file("cube.msh")
    model.stretch('x', 1.3)
    model.calculateAccelerations()
    print(model.nodeAccelerations)
    makeVTKSnapshot(model, 0)

main()