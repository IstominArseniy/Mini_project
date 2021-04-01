class Mesh:
    def __init__(self, nodeNumber):
        self.nodeNumber = nodeNumber
        self.nodeConnections = [[] for i in range(nodeNumber)]
        self.nodeInitialCoordinates = [[0.0, 0.0, 0.0] for i in range(nodeNumber)]
        self.nodeCoordinates = [[0.0, 0.0, 0.0] for i in range(nodeNumber)]
        self.nodeVelocities = [[0.0, 0.0, 0.0] for i in range(nodeNumber)]
        self.nodeAccelerations = [[0.0, 0.0, 0.0] for i in range(nodeNumber)]
        self.tetrList = []
        self.k = 1
        self.b = 0.1
        self.m = 1
        self.dt = 0.01

    def calculateAccelerations(self):
        for i in range(self.nodeNumber):
            Fx = Fy = Fz = 0.0
            for j in range(len(self.nodeConnections[i])):
                x1 = self.nodeCoordinates[i][0]
                y1 = self.nodeCoordinates[i][1]
                z1 = self.nodeCoordinates[i][2]
                x2 = self.nodeCoordinates[self.nodeConnections[i][j]][0]
                y2 = self.nodeCoordinates[self.nodeConnections[i][j]][1]
                z2 = self.nodeCoordinates[self.nodeConnections[i][j]][2]
                x10 = self.nodeInitialCoordinates[i][0]
                y10 = self.nodeInitialCoordinates[i][1]
                z10 = self.nodeInitialCoordinates[i][2]
                x20 = self.nodeInitialCoordinates[self.nodeConnections[i][j]][0]
                y20 = self.nodeInitialCoordinates[self.nodeConnections[i][j]][1]
                z20 = self.nodeInitialCoordinates[self.nodeConnections[i][j]][2]
                delta = ((x1 - x10 + x20 - x2) ** 2 + (y1 - y10 + y20 - y2) ** 2 + (z1 - z10 + z20 - z2) ** 2) ** 0.5
                Fx += (delta * self.k) * (x2 - x1) / ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5 - self.b * self.nodeVelocities[i][0]
                Fy += (delta * self.k) * (y2 - y1) / ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5 - self.b * self.nodeVelocities[i][1]
                Fz += (delta * self.k) * (z2 - z1) / ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5 - self.b * self.nodeVelocities[i][2]
            self.nodeAccelerations[i][0] = Fx / self.m
            self.nodeAccelerations[i][1] = Fy / self.m
            self.nodeAccelerations[i][2] = Fz / self.m

    def update(self):
        for i in range(self.nodeNumber):
            self.nodeCoordinates[i][0] = self.dt ** 2 / 2 * self.nodeAccelerations[i][0] + self.dt * self.nodeVelocities[i][0]
            self.nodeCoordinates[i][1] = self.dt ** 2 / 2 * self.nodeAccelerations[i][1] + self.dt * self.nodeVelocities[i][1]
            self.nodeCoordinates[i][2] = self.dt ** 2 / 2 * self.nodeAccelerations[i][2] + self.dt * self.nodeVelocities[i][2]
            self.nodeVelocities[i][0] = self.dt * self.nodeAccelerations[i][0]
            self.nodeVelocities[i][1] = self.dt * self.nodeAccelerations[i][1]
            self.nodeVelocities[i][2] = self.dt * self.nodeAccelerations[i][2]

    def stretch(self, direction, strength):
        """
        stretch model(multiply coordinates by number strngth)
        :param direction: 'x', 'y', 'z' - direction of stretching
        """
        for i in range(self.nodeNumber):
            if direction == 'x':
                self.nodeCoordinates[i][0] = self.nodeInitialCoordinates[i][0] * strength
            if direction == 'y':
                self.nodeCoordinates[i][1] = self.nodeInitialCoordinates[i][1] * strength
            if direction == 'z':
                self.nodeCoordinates[i][2] = self.nodeInitialCoordinates[i][2] * strength
