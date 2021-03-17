library(igraph)

# CREAR GRAF
g1 <- graph(c(1,2 ,1,3, 2,3, 3,5), n=5)
V(g1)
E(g2)

# CREAR GRAFS FORMA DIFERENT
g2 <- graph.empty() + vertices(letters[1:10], color="red")
g2 <- g2 + vertices(letters[11:20], color="blue")
g2 <- g2 + edges(sample(V(g), 30, replace=TRUE), color="green")
E(g2)

# CREAR GRAFS DESDE UN FITXER (paths absoluts)
g3 <- read.graph("/home/tomeu/Desktop/Uni/CAIM-FIB/Lab7/edges.txt")
V(g3)
E(g3)

# GENERAR GRAFS
er_graph <- erdos.renyi.game(100, 2/100)
ws_graph <- watts.strogatz.game(1, 100, 4, 0.05)
ba_graph <- barabasi.game(100)

# PINTAR GRAFS
plot(er_graph, vertex.label=NA, vertex.size=3)
plot(ws_graph, layout=layout.circle, vertex.label=NA, vertex.size=3)
plot(ba_graph, vertex.label=NA, vertex.size=3)

# PINTAR GRAFS AMB DIFRENTS CARACTERISTIQUES

g <- graph.lattice( c(10,10) )
E(g)$weight <- runif(ecount(g))
E(g)$color <- "grey"
E(g)[ weight > 0.9 ]$color <- "red"
plot(g, vertex.size=2, vertex.label=NA, layout=layout.kamada.kawai,
edge.width=2+3*E(g)$weight)
