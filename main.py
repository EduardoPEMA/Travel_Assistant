import sys
import os
import json
import pathlib
import operator
from random import randint
from travel_assistant import *
from PySide2.QtWidgets import QGraphicsScene
from PySide2.QtCore import Slot
from PySide2.QtGui import QPen, QColor, QTransform


class mainWindow(QMainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()

        # Data control
        self.database = dict()
        self.countries = dict()
        self.users = dict()
        self.graphOfCountries = dict()
        self.path = str(pathlib.Path(__file__).parent.absolute()) + '/database.json'

        # Ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showMaximized()

        # Views control
        self.ui.views.setCurrentIndex(0)
        self.ui.travel_button.clicked.connect(self.changePage)
        self.ui.ready_button.clicked.connect(self.changePage)
        self.ui.adventure_button.clicked.connect(self.changePage)
        self.ui.personalized_button.clicked.connect(self.changePage)
        self.ui.countries_button.clicked.connect(self.changePage)
        self.ui.backbutton_1.clicked.connect(self.changePage)
        self.ui.backbutton_2.clicked.connect(self.changePage)
        self.ui.backbutton_3.clicked.connect(self.changePage)
        self.ui.backbutton_4.clicked.connect(self.changePage)

        # Manage stars
        self.ui.clothes_sb.valueChanged.connect(self.manageStars)
        self.ui.food_sb.valueChanged.connect(self.manageStars)
        self.ui.places_sb.valueChanged.connect(self.manageStars)

        # Graphics
        self.scene = QGraphicsScene()
        self.pen = QPen()
        self.ui.gvWorldMap.setScene(self.scene)

        # Functions
        self.loadData()
        self.drawMap()
        self.initStars()

        # Connections
        self.ui.start_button.clicked.connect(self.manageMap)
        self.ui.cancel_button.clicked.connect(self.manageMap)
        self.ui.btnResetMap.clicked.connect(self.resetMap)
        self.ui.departure.setCurrentIndex(-1)
        self.ui.arrival.setCurrentIndex(-1)

    def loadData(self):
        if os.path.exists(self.path) and os.stat(self.path).st_size != 0:
            with open(self.path, 'r') as data_file:
                self.database = json.load(data_file)
                self.users = self.database["Users"]
                self.countries = self.database["Countries"]

        for country in self.countries:
            self.ui.departure.addItem(country["name"])
            self.ui.arrival.addItem(country["name"])
    # loadData

    def saveData(self):
        self.database["Users"] = self.users
        self.database["Countries"] = self.countries
        with open(self.path, 'w') as data_file:
            json.dump(self.database, data_file, indent=5)
    # saveData

    def changePage(self):
        if self.sender().objectName() == "travel_button":
            self.ui.views.setCurrentIndex(1)
        elif self.sender().objectName() == "ready_button":
            self.addNewUser()
            self.ui.arrival.setDisabled(True)
            self.resetMap()
            self.ui.views.setCurrentIndex(3)
        elif self.sender().objectName() == "personalized_button":
            self.ui.views.setCurrentIndex(3)
        elif self.sender().objectName() == "adventure_button":
            self.ui.views.setCurrentIndex(2)
        elif self.sender().objectName() == "countries_button":
            self.ui.views.setCurrentIndex(4)
        elif self.sender().objectName() == "backbutton_1":
            self.ui.views.setCurrentIndex(0)
        elif self.sender().objectName() == "backbutton_2":
            self.ui.views.setCurrentIndex(1)
        elif self.sender().objectName() == "backbutton_3":
            self.clearMap()
            self.ui.arrival.setEnabled(True)
            self.ui.views.setCurrentIndex(1)
        elif self.sender().objectName() == "backbutton_4":
            self.ui.views.setCurrentIndex(3)
    # changePage

    def manageMap(self):
        if self.sender().objectName() == "start_button":
            self.scene.clear()
            self.drawMap()
            self.showDijkstra()
        else:
            self.clearMap()
    # manageMap

    def initStars(self):
        for i in range(1, 4):
            for j in range(2, 6):
                command = "self.ui.star{}_{}.hide()".format(i, j)
                exec(command)
    # initStars

    def manageStars(self):
        if self.sender().objectName() == "places_sb":
            for i in range(2, 6):
                command = "self.ui.star1_{}.hide()".format(i)
                exec(command)

            for i in range(2, int(self.ui.places_sb.text()) + 1):
                command = "self.ui.star1_{}.show()".format(i)
                exec(command)

        elif self.sender().objectName() == "food_sb":
            for i in range(2, 6):
                command = "self.ui.star2_{}.hide()".format(i)
                exec(command)

            for i in range(2, int(self.ui.food_sb.text()) + 1):
                command = "self.ui.star2_{}.show()".format(i)
                exec(command)

        elif self.sender().objectName() == "clothes_sb":

            for i in range(2, 6):
                command = "self.ui.star3_{}.hide()".format(i)
                exec(command)

            for i in range(2, int(self.ui.clothes_sb.text()) + 1):
                command = "self.ui.star3_{}.show()".format(i)
                exec(command)
    # manageStars

    def addNewUser(self):

        name = self.ui.nameText.text()
        budget = int(self.ui.budgetText.text())
        places = int(self.ui.places_sb.text())
        food = int(self.ui.food_sb.text())
        clothes = int(self.ui.clothes_sb.text())

        self.users[name] = dict()
        self.users[name]["budget"] = budget
        self.users[name]["food"] = food
        self.users[name]["places"] = places
        self.users[name]["clothes"] = clothes
        self.saveData()
    # addNewUser

    @Slot()
    def drawMap(self):
        self.graphOfCountries.clear()
        self.pen.setWidth(1)
        self.pen.setColor(QColor(0, 0, 0))
        self.scene.addEllipse(0, 0, 1, 1, self.pen)
        self.scene.addEllipse(948, 445, 1, 1, self.pen)

        font = QFont()
        font.setPixelSize(8)

        for node in self.countries:
            origin = (node["coordinates"][0], node["coordinates"][1])
            if origin not in self.graphOfCountries:
                self.graphOfCountries[origin] = []
            for adjacencies in node["adjacencies"]:
                self.graphOfCountries[origin].append(adjacencies)

        # distances = []
        # for data, list in self.graphOfCountries.items():
            # for data2 in list:
                # distances.append(["$" + str(data2[1]), (data[0] + data2[0][0]) / 2, (data[1] + data2[0][1]) / 2])

        # for d1 in distances:
            # for d2 in distances:
                # if d1 != d2:
                    # if d1[1] == d2[1] and d1[2] == d2[2]:
                        # d2[1] = d2[1] - 7
                        # d2[2] = d2[2] - 7

        for country, adjacencies in self.graphOfCountries.items():
            self.pen.setWidth(5)
            r = randint(0, 200)
            g = randint(0, 200)
            b = randint(0, 200)
            color = QColor(r, g, b)
            self.pen.setColor(color)
            self.scene.addEllipse(country[0], country[1], 5, 5, self.pen)
            self.pen.setWidth(3)
            for element in adjacencies:
                otherCountry = element[0]
                self.scene.addLine(country[0] + 1, country[1] + 1, otherCountry[0] + 1, otherCountry[1] + 1, self.pen)
                # dataD = distances.pop(0)
                # distance = self.scene.addText(dataD[0], font)
                # distance.setX(dataD[1])
                # distance.setY(dataD[2])
    # drawMap

    @Slot()
    def showDijkstra(self):
        departureName = self.ui.departure.currentText()
        arrivalName = self.ui.arrival.currentText()
        initialNode = ()
        finalNode = ()

        if self.ui.arrival.isEnabled() == False:
            userBudget = int(self.ui.budgetText.text())
        else:
            userBudget = 0

        for country in self.countries:
            if country["name"] == arrivalName:
                finalNode = (country["coordinates"][0], country["coordinates"][1])
            if country["name"] == departureName:
                initialNode = (country["coordinates"][0], country["coordinates"][1])

        if initialNode in self.graphOfCountries:
            distancesArray = dict()
            ordenedList = []
            wayArray = dict()

            ordenedList.append((initialNode, 0))
            for node in self.graphOfCountries:
                if node == initialNode:
                    distancesArray[node] = 0
                else:
                    distancesArray[node] = 9999999

            flag = True
            while ordenedList and flag:
                auxNode = ordenedList.pop(0)
                for element in self.graphOfCountries[auxNode[0]]:
                    nodeWithDistance = ((element[0][0], element[0][1]), element[1])
                    destinyDistance = distancesArray.get(nodeWithDistance[0])
                    currentDistance = nodeWithDistance[1] + auxNode[1]

                    if currentDistance < destinyDistance:
                        distancesArray[nodeWithDistance[0]] = currentDistance
                        wayArray[nodeWithDistance[0]] = auxNode[0]
                        ordenedList.append((nodeWithDistance[0], currentDistance))

                        ordenedList = [(b, a) for a, b in ordenedList]
                        ordenedList.sort()
                        ordenedList = [(a, b) for b, a in ordenedList]

                    if nodeWithDistance[0] == finalNode:
                        flag = False
                        break

            if flag:
                distancesArray_Sort = sorted(distancesArray.items(), key=operator.itemgetter(1))
                for i in range(len(distancesArray_Sort)):
                    if (i+1) != len(distancesArray_Sort):
                        if userBudget >= distancesArray_Sort[i][1] \
                                and userBudget <= distancesArray_Sort[i + 1][1]:
                            finalNode = distancesArray_Sort[i][0]
                            break
                    else:
                        finalNode = distancesArray_Sort[i][0]

            dijkstraGraph = dict()
            self.fillDijkstraGraph(finalNode, initialNode, wayArray, dijkstraGraph)
            self.printGraph(dijkstraGraph)
            self.scene.addEllipse(initialNode[0], initialNode[1], 6, 6, self.pen)
    # showDijkstra

    def fillDijkstraGraph(self, node, initialNode, wayArray, dijkstraGraph):
        if node != initialNode:

            for data in self.graphOfCountries[node]:
                nodeOfGCountries = (data[0][0], data[0][1])
                if nodeOfGCountries == wayArray[node]:
                    dijkstraGraph[node] = nodeOfGCountries
            self.fillDijkstraGraph(wayArray[node], initialNode, wayArray, dijkstraGraph)
    # fillDijkstraGraph

    def printGraph(self, auxGraph):
        self.pen.setWidth(5)
        color = QColor(255, 0, 0)
        self.pen.setColor(color)
        first = True
        totalCost = 0
        self.ui.listWidget.clear()

        auxGraph_sort = []
        for node1, node2 in auxGraph.items():
            auxGraph_sort.append((node1,node2))
        auxGraph_sort.reverse()
        auxGraph_sort = [(n1, n2) for n2, n1 in auxGraph_sort]
        path = []
        auxStr = ""
        for vertice, otherVertice in auxGraph_sort:
            self.scene.addEllipse(vertice[0], vertice[1], 6, 6, self.pen)
            self.scene.addEllipse(otherVertice[0], otherVertice[1], 6, 6, self.pen)
            self.scene.addLine(vertice[0] + 3, vertice[1] + 3,
                               otherVertice[0] + 3, otherVertice[1] + 3, self.pen)

            # This puts the names of the countries in the list
            for elem in self.countries:

                # conditional that writes the first country of the graph
                if first and elem["coordinates"][0] == vertice[0] and elem["coordinates"][1] == vertice[1]:
                    aux = str(elem["name"]) + ':'
                    auxStr = aux
                    path.append(aux)
                    first = False

                elif otherVertice[0] == elem["coordinates"][0] and otherVertice[1] == elem["coordinates"][1]:
                    for data in self.countries:
                        coordinatesOfData = (data["coordinates"][0],data["coordinates"][1])
                        if coordinatesOfData == vertice:
                            for adj in data["adjacencies"]:
                                if otherVertice[0] == adj[0][0] and otherVertice[1] == adj[0][1]:
                                    aux = str('    ' + elem["name"]) + '  -  $' + str(adj[1])
                                    totalCost += adj[1]
                                    path.append(aux)
                                    break
                            break
        aux = "\nTotal cost: $" + str(totalCost)
        for dataCnt in range(len(path)):
            if path[dataCnt] == auxStr:
                self.ui.listWidget.addItem(path.pop(dataCnt))
                break
        for value in path:
            self.ui.listWidget.addItem(value)
        self.ui.listWidget.addItem(aux)
    # printGraph

    def wheelEvent(self, event):
        if (event.delta() > 0):
            self.ui.gvWorldMap.scale(1.2, 1.2)
        else:
            self.ui.gvWorldMap.scale(0.8, 0.8)
    # wheelEvent

    @Slot()
    def resetMap(self):
        self.ui.gvWorldMap.setTransform(QTransform())
        # self.scene.clear()
        # self.drawMap()
    # resetMap

    @Slot()
    def clearMap(self):
        self.ui.gvWorldMap.setTransform(QTransform())
        self.scene.clear()
        self.drawMap()
        self.ui.listWidget.clear()
        self.ui.departure.setCurrentIndex(-1)
        self.ui.arrival.setCurrentIndex(-1)
    # clearMap


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())
