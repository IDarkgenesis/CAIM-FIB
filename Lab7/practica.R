# TASK 1

# CREAR SAMPLES PER PLOT

# If we want a value that starts with p = 0.000x we need to select two numbers such that nSamples/div == 4
nSamples = 15
div = nSamples/4

prob <- seq(nSamples)
index <- 1

for(i in (nSamples-1):0){
  prob[index] <- 10 ** -(i/div)
  index <- index + 1
}
prob

avShortPath <- seq(nSamples)
clustCoeff <- seq(nSamples)

index <- 1
for(i in prob) {
  ws <- watts.strogatz.game(1, 1000, 4, i)
  
  avShortPath[index] <- average.path.length(ws)
  avShortPath[index] <- avShortPath[index]/avShortPath[1]
  
  clustCoeff[index] <- transitivity(ws)
  clustCoeff[index] <- clustCoeff[index]/clustCoeff[1]
  
  index <- index + 1
}

avShortPath
