import numpy as np

def binarySearch(elem, l, r, list):
    if l > r:
        return -1
    p= (l+r) // 2
    if elem == list[p]:
        return p
    if greaterElem(elem, list[p]):
        return binarySearch(elem, p+1, r, list)
    else:
        return binarySearch(elem, l, p-1, list)

def greaterElem(e1, e2):
    minSize = min(len(e1),len(e2))
    for i in range(minSize):
        if e1[i] != e2[i]:
            return e1[i] > e2[i]
    return False

def normalize(tw):
    """
    Normalizes the weights in t so that they form a unit-length vector
    It is assumed that not all weights are 0
    :param tw:
    :return:
    """
    #
    norm = np.sqrt(sum(x**2 for (_,x) in tw))
    print(norm)
    normalizedVec=[]
    for (t,w) in tw:
        print(t, w)
        normalizedVec.append((t,w/norm))
    
    return normalizedVec


numElem= int(input("Number of elements\n"))

list = []
for _ in range(numElem):
    list.append(("a",int(input())))

print(normalize(list))