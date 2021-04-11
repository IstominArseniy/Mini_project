import math
import gmsh
GMSH_LINE_CODE = 1
GMSH_TETR_CODE = 4


class Model:
    def __init__(self, file_name, k=1, b=1, m=1, dt=0.3):
        # simulation params
        self.k = k
        self.b = b
        self.m = m
        self.dt = dt
        # reading
        gmsh.initialize()
        gmsh.open(file_name)
        nodeTags, nodesCoord, parametricCoord = gmsh.model.mesh.getNodes()  # nodesCoord - массив длинной 3 * n - x1, y1, z1, ...
        tetrNodeTags = None
        elementTypes, elementTags, elementNodeTags = gmsh.model.mesh.getElements()
        # elementTypes - вектор, показывающий, какие типы элементов вообще есть (и в каком порядке лежат в следующих массивах)
        # elementsTags - массив массивов тэгов соответствующих элементов(элемент - штука из nodes)
        # elementNodeTags - массив массивов тэгов нод, соответствующих элементам (подряд: количество элементов * нод на элемент)
        # извлечем данные об отрезках в массив tetrNodeTags
        for i in range(len(elementTypes)):
            if elementTypes[i] == GMSH_TETR_CODE:
                tetrNodeTags = elementNodeTags[i]
                break
        # теперь в tetrNodeTags лежат подряд 4ки тэгов нод, образующих тетраэдры
        # создадим словарь соответствия порядкового номера в nodeTags и самих nodeTags
        meshIds = {}
        for i in range(len(nodeTags)):
            meshIds[nodeTags[i]] = i
        # создадим и заполним словарь nodeConnection: nodeConnection[i] = [ноды, с которыми соединена данная]
        nodeConnections = {}
        for i in nodeTags:
            nodeConnections[i] = set()
        for i in range(0, len(tetrNodeTags), 4):
            for j in range(4):
                for k in range(4):
                    if k != j:
                        nodeConnections[tetrNodeTags[i + k]].add(meshIds[tetrNodeTags[i + j]])
        # создадим и заполним словарь nodeCoordinates: nodeCoordinates[i] = [x_i, y_i, z_i]
        nodeCoordinates = {}
        # for i in range(0, len(nodeTags)):
        #    nodeCoordinates = tuple()
        for i in range(0, len(nodeTags)):
            nodeCoordinates[nodeTags[i]] = [nodesCoord[i * 3], nodesCoord[i * 3 + 1], nodesCoord[i * 3 + 2]]
        # print(nodeConnections)
        # print(nodeCoordinates)
        gmsh.finalize()
        nodeNumber = len(nodeTags)
        self.nodeNumber = nodeNumber
        self.nodeConnections = [[] for i in range(nodeNumber)]
        self.nodeInitialCoordinates = [[0.0, 0.0, 0.0] for i in range(nodeNumber)]
        self.nodeCoordinates = [[0.0, 0.0, 0.0] for i in range(nodeNumber)]
        self.nodeVelocities = [[0.0, 0.0, 0.0] for i in range(nodeNumber)]
        self.nodeAccelerations = [[0.0, 0.0, 0.0] for i in range(nodeNumber)]
        self.tetrList = []

        for i in range(0, len(tetrNodeTags), 4):
            self.tetrList.append([meshIds[tetrNodeTags[i]], meshIds[tetrNodeTags[i + 1]], meshIds[tetrNodeTags[i + 2]],
                                  meshIds[tetrNodeTags[i + 3]]])
        for i in range(len(nodeTags)):
            self.nodeInitialCoordinates[i] = nodeCoordinates[nodeTags[i]].copy()
            self.nodeCoordinates[i] = nodeCoordinates[nodeTags[i]].copy()
            self.nodeConnections[i] = list(nodeConnections[nodeTags[i]]).copy()

        self.name = file_name[:-4]

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
                l = ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5
                l_0 = ((x20 - x10) ** 2 + (y20 - y10) ** 2 + (z20 - z10) ** 2) ** 0.5
                delta = l - l_0
                Fx += (delta * self.k) * (x2 - x1) / l - self.b * self.nodeVelocities[i][0]
                Fy += (delta * self.k) * (y2 - y1) / l - self.b * self.nodeVelocities[i][1]
                Fz += (delta * self.k) * (z2 - z1) / l - self.b * self.nodeVelocities[i][2]
            self.nodeAccelerations[i][0] = Fx / self.m
            self.nodeAccelerations[i][1] = Fy / self.m
            self.nodeAccelerations[i][2] = Fz / self.m

    def update(self):
        for i in range(self.nodeNumber):
            self.nodeCoordinates[i][0] += (self.dt ** 2 / 2 * self.nodeAccelerations[i][0] + self.dt * self.nodeVelocities[i][0])
            self.nodeCoordinates[i][1] += (self.dt ** 2 / 2 * self.nodeAccelerations[i][1] + self.dt * self.nodeVelocities[i][1])
            self.nodeCoordinates[i][2] += (self.dt ** 2 / 2 * self.nodeAccelerations[i][2] + self.dt * self.nodeVelocities[i][2])
            self.nodeVelocities[i][0] += (self.dt * self.nodeAccelerations[i][0])
            self.nodeVelocities[i][1] += (self.dt * self.nodeAccelerations[i][1])
            self.nodeVelocities[i][2] += (self.dt * self.nodeAccelerations[i][2])

    def stretch(self, direction, strength):
        """
        stretch model(multiply coordinates by number strngth)
        :param direction: 'x', 'y', 'z' - direction of stretching
        """
        for i in range(self.nodeNumber):
            if direction == 'x':
                tmp = self.nodeInitialCoordinates[i][0]
                self.nodeCoordinates[i][0] = tmp * strength
            if direction == 'y':
                self.nodeCoordinates[i][1] = self.nodeInitialCoordinates[i][1] * strength
            if direction == 'z':
                self.nodeCoordinates[i][2] = self.nodeInitialCoordinates[i][2] * strength


    def getPointCoord(self, id):
        return self.nodeCoordinates[id]