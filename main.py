from libConnector import*
from MeshClass import Mesh


def main():
    model = read_msh_file("cube.msh")
    makeVTKSnapshot(model, 0)

