import gmsh
import vtk
from MeshClass import Mesh
GMSH_LINE_CODE = 1
GMSH_TETR_CODE = 4


def read_msh_file(file_name):
    """
    Берет на вход .msh файл, выделят из него словарь со связями с другими точками и словарь нод с координатами и создает объект mesh
    """
    gmsh.initialize()
    gmsh.open(file_name)
    nodeTags, nodesCoord, parametricCoord = gmsh.model.mesh.getNodes()  # nodesCoord - массив длинной 3 * n - x1, y1, z1, ...
    tetrNodeTags = None
    elementTypes, elementTags, elementNodeTags = gmsh.model.mesh.getElements()
    # elementTypes - вектор, показывающий, какие типы элементов вообще есть (и в каком порядке лежат в следующих массивах)
    # elementsTags - массив массивов тэгов соответствующих элементов(элемент - штука из nodes)
    # elementNodeTags - массив массивов тэгов нод, соответствующих элементам (тупо подряд: количество элементов * нод на элемент)
    # извлечем данные об отрезках в массив tetrNodeTags
    for i in range(len(elementTypes)):
        if elementTypes[i] == GMSH_TETR_CODE:
            tetrNodeTags = elementNodeTags[i]
            break
    # теперь в tetrNodeTags лежат подряд 4ки тэгов нод, образующих тетраэдры
    # создадим и заполним словарь nodeConnection: nodeConnection[i] = [ноды, с которыми соединена данная]
    nodeConnections = {}
    for i in nodeTags:
        nodeConnections[i] = set()
    for i in range(0, len(tetrNodeTags), 4):
        for j in range(4):
            for k in range(4):
                if k != j:
                    nodeConnections[tetrNodeTags[i + k]].add(tetrNodeTags[i + j])
    # создадим и заполним словарь nodeCoordinates: nodeCoordinates[i] = [x_i, y_i, z_i]
    nodeCoordinates = {}
    # for i in range(0, len(nodeTags)):
    #    nodeCoordinates = tuple()
    for i in range(0, len(nodeTags)):
        nodeCoordinates[nodeTags[i]] = [nodesCoord[i * 3], nodesCoord[i * 3 + 1], nodesCoord[i * 3 + 2]]
    # print(nodeConnections)
    # print(nodeCoordinates)
    gmsh.finalize()
    mesh = Mesh(len(nodeTags))
    # создадим словарь соответствия порядкового номера в nodeTags и самих nodeTags
    meshIds = {}
    for i in range(len(nodeTags)):
        meshIds[nodeTags[i]] = i
    # заполним mesh.tetrList
    print(meshIds)
    for i in range(0, int(len(tetrNodeTags) / 4), 4):
        j = int(i / 4)
        mesh.tetrList.append([meshIds[tetrNodeTags[j]], meshIds[tetrNodeTags[j + 1]], meshIds[tetrNodeTags[j + 2]], meshIds[tetrNodeTags[j + 3]]])
    print(mesh.tetrList)
    for i in range(len(nodeTags)):
        mesh.nodeInitialCoordinates[i] = nodeCoordinates[nodeTags[i]]
        mesh.nodeCoordinates[i] = nodeCoordinates[nodeTags[i]]
        mesh.nodeConnections[i] = list(nodeConnections[nodeTags[i]])
    return mesh


def makeVTKSnapshot(mesh, snapNumber):
    """
    create vtk snapshot from mesh (Mesh object)
    save coordinates of nodes, velocities and accelerations
    """
    # VTK сетка
    unstructuredGrid = vtk.vtkUnstructuredGrid()
    points = vtk.vtkPoints()
    velocities = vtk.vtkDoubleArray()
    velocities.SetName("velocities")
    accelerations = vtk.vtkDoubleArray()
    accelerations.SetName("accelerations")
    for i in range(mesh.nodeNumber):
        points.InsertNextPoint(mesh.nodeCoordinates[i][0], mesh.nodeCoordinates[i][1], mesh.nodeCoordinates[i][2])
        velocities.InsertNextTouple(mesh.nodeVelocities[i][0], mesh.nodeVelocities[i][1], mesh.nodeVelocities[i][2])
        accelerations.InsertNextTouple(mesh.nodeAccelerations[i][0], mesh.nodeAccelerations[i][1], mesh.nodeAccelerations[i][2])
    # добавление точек и полей в сетку
    unstructuredGrid.SetPoints(points)
    unstructuredGrid.GetPointData().AddArray(velocities)
    unstructuredGrid.GetPointData().AddArray(accelerations)
    # описание тетраэдров в терминах vtk
    for i in range(len(mesh.tetrList)):
        tetr = vtk.vtkTetra()
        for j in range(4):
            tetr.GetPointIds().SetId(j, mesh.tetrList[i][j])
        unstructuredGrid.InsertNextCell(tetr.GetCellType(), tetr.GetPointIds())
    # формировка фалйла
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetInputDataObject(unstructuredGrid)
    writer.SetFileName("model" + str(snapNumber) + ".vtu")
    writer.Write()

read_msh_file("cube.msh")