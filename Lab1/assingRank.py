path=input("Path de fitxer per assignar rank\n")
f = open(path,'r')
numElements= int(f.readline())
previous=0
rank=0
for i in range(0,numElements):
    appraitions= int(f.readline())
    if appraitions != previous:
        rank += 1
        previous = appraitions
    print(rank)