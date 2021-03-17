#!/usr/bin/python

from collections import namedtuple
import time
import sys
import operator

class Edge:
    def __init__ (self, origin=None):
        self.origin = ... # i
        self.weight = 1  # K
        self.index = 0 
    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)
        
    ## write rest of code that you need for this class

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight = 0  # write appropriate value
        self.index = 0
        self.pageIndex = -1

    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}\n"
    

edgeList = [] # list of Edge
edgeHash = dict() # hash of edge to ease the match
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport

pesosFinals = []
noOuts = 0

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r");
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            # Assignar a dict posició de aeroport a la llista
            airportHash[a.code] = cont
            a.index = cont
            cont += 1
            airportList.append(a)
            
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")


def readRoutes(fd):
    print("Reading Routes file from {fd}")
    # write your code
    routesTxt = open(fd, "r");
    cont = 0

    for line in routesTxt.readlines():
        e = Edge()
        try:
            temp = line.split(',')
            if len(temp[2]) != 3 or len(temp[4]) != 3 or temp[2] not in airportHash or temp[4] not in airportHash:           
                raise Exception('not an IATA code or Valid Airport')
            
            indexDesti = airportHash[temp[4]]
            indexOrigen = airportHash[temp[2]]
            
            aeroportDesti = airportList[indexDesti]
            aeroportOrigen = airportList[indexOrigen]
            
            if temp[2] not in aeroportDesti.routeHash:
                e.origin = aeroportOrigen.code
                e.index = indexOrigen
                aeroportDesti.routes.append(e)
                aeroportDesti.routeHash[temp[2]] = len(aeroportDesti.routes) - 1
            else:
                aeroportDesti.routes[aeroportDesti.routeHash[temp[2]]].weight += 1
            
            aeroportOrigen.outweight += 1

        except Exception as inst:
            pass

        

def checkError(P, Q, error):
    for i in range(len(P)):
        if (abs(P[i] - Q[i]) > error):
            return False
    return True
    

def computePageRanks():
    N = len(airportList)
    P = [1/N for _ in range(N)]
    L = 0.9

    # El que aporta cada node que té 0 outweight
    aportacioOuts = 1/N * noOuts
    aportacioOuts = aportacioOuts / N
    aux = 1/N
    maxIterations = 1000
    iteration = 0
    error = 0.000000005
    end = False
    while iteration < maxIterations and not end:
        Q = [0 for _ in range(N)]
        for i in range(N):
            auxSum = 0
            for edge in airportList[i].routes:
                auxSum += P[edge.index] * edge.weight / airportList[edge.index].outweight
            Q[i] = L * auxSum + (1-L)/N + aportacioOuts
        
        #print(sum(Q))
        
        if checkError(P,Q,error):
            end = True
        P = Q
        iteration += 1

    global pesosFinals
    pesosFinals = P
    return iteration

def outputPageRanks():
    # write your code
    for i in range(len(pesosFinals)):
        airportList[i].pageIndex = pesosFinals[i]

    aux=sorted(airportList, key=lambda elem: elem.pageIndex, reverse= True)
    
    for i in range(len(aux)):
        aux[i].pageIndex = i+1

    print(aux)


def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")

    global noOuts
    for air in airportList:
        if air.outweight == 0:
            noOuts += 1

    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2-time1)


if __name__ == "__main__":
    sys.exit(main())
