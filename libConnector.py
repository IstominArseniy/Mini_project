import gmsh
import vtk
import os
from ModelClass import Model
GMSH_LINE_CODE = 1
GMSH_TETR_CODE = 4


def makeVTKSnapshot(mesh, snapNumber):
    """
    create vtk snapshot from mesh (Mesh object)
    save coordinates of nodes, velocities and accelerations
    """
    # VTK сетка
    unstructuredGrid = vtk.vtkUnstructuredGrid()
    points = vtk.vtkPoints()
    velocities = vtk.vtkDoubleArray()
    velocities.SetNumberOfComponents(3)
    velocities.SetName("velocities")
    accelerations = vtk.vtkDoubleArray()
    accelerations.SetNumberOfComponents(3)
    accelerations.SetName("accelerations")
    for i in range(mesh.nodeNumber):
        points.InsertNextPoint(mesh.nodeCoordinates[i][0], mesh.nodeCoordinates[i][1], mesh.nodeCoordinates[i][2])
        velocities.InsertNextTuple((mesh.nodeVelocities[i][0], mesh.nodeVelocities[i][1], mesh.nodeVelocities[i][2]))
        accelerations.InsertNextTuple((mesh.nodeAccelerations[i][0], mesh.nodeAccelerations[i][1], mesh.nodeAccelerations[i][2]))
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
    if not os.path.exists(mesh.name):
        print(mesh.name)
        os.mkdir(mesh.name)
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetInputDataObject(unstructuredGrid)
    writer.SetFileName(mesh.name + "/" + mesh.name + str(snapNumber) + ".vtu")
    writer.Write()

#  read_msh_file("cube.msh")