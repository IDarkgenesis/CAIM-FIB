#!/bin/bash

if [ $# -eq 6 ]
then
    echo
    echo "Extracting data"

    python3 ExtractData.py --index $1 --minfreq $2 --maxfreq $3 --numwords $4
    
    echo
    echo "Data extracted"
    echo
    echo "Generating prototypes"
    
    python3 GeneratePrototypes.py --nclust $5
    
    echo
    echo "Prototypes generated"
    echo
    echo "Executing MRKmeans"
    echo
    python3 MRKmeans.py --ncores $6

else
    echo
    echo "Wrong number of parameters"
    
    echo
    echo "Usage: executarTests.sh <index> <minfreq> <maxfreq> <numwords> <nclust> <num-cores>"
    
    echo
    echo "First parameter must be the   INDEX       for ExtractData.py"
    echo "Second parameter must be the  MINFREQ     for ExtractData.py"
    echo "Third parameter must be the   MAXFREQ     for ExtractData.py"
    echo "Fourth parameter must be the  NUMWORDS    for ExtractData.py"
    echo "Fifth parameter must be the   NCLUST      for GeneratePrototypes.py"
    echo "Sixth parameter must be the   NUM-CORES   for MRKmeans.py"
    
    echo
    
    fi
