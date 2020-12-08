"""
.. module:: MRKmeansDef

MRKmeansDef
*************

:Description: MRKmeansDef

    

:Authors: bejar
    

:Version: 

:Created on: 17/07/2017 7:42 

"""

from mrjob.job import MRJob
from mrjob.step import MRStep

__author__ = 'bejar'


class MRKmeansStep(MRJob):
    prototypes = {}

    def jaccard(self, prot, doc):
        """
        Compute here the Jaccard similarity between  a prototype and a document
        prot should be a list of pairs (word, probability)
        doc should be a list of words
        Words must be alphabeticaly ordered

        The result should be always a value in the range [0,1]
        """

        intersecSize = sum(1 for elem in prot if elem[0] in doc)
        unionSize = len(prot) + len(doc)

        return intersecSize / float(unionSize - intersecSize)

    def configure_args(self):
        """
        Additional configuration flag to get the prototypes files

        :return:
        """
        super(MRKmeansStep, self).configure_args()
        self.add_file_arg('--prot')

    def load_data(self):
        """
        Loads the current cluster prototypes

        :return:
        """
        f = open(self.options.prot, 'r')
        for line in f:
            cluster, words = line.split(':')
            cp = []
            for word in words.split():
                cp.append((word.split('+')[0], float(word.split('+')[1])))
            self.prototypes[cluster] = cp

    def assign_prototype(self, _, line):
        """
        This is the mapper it should compute the closest prototype to a document

        Words should be sorted alphabetically in the prototypes and the documents

        This function has to return at list of pairs (prototype_id, document words)

        You can add also more elements to the value element, for example the document_id
        """

        # Each line is a string docid:wor1 word2 ... wordn
        doc, words = line.split(':')
        lwords = words.split()

        #
        # Compute map here
        # 
        closestDistance = -1
        closestClust = "ErrorIfSame"

        for currCluster in self.prototypes:
            
            auxDist = self.jaccard(self.prototypes[currCluster], lwords)
            
            if (closestDistance < 0) or (auxDist < closestDistance):
                
                closestClust = currCluster
                closestDistance = auxDist

        # Return pair key, value
        yield closestClust, (doc, lwords)

    def aggregate_prototype(self, key, values):
        """
        input is cluster and all the documents it has assigned
        Outputs should be at least a pair (cluster, new prototype)

        It should receive a list with all the words of the documents assigned for a cluster

        The value for each word has to be the frequency of the word divided by the number
        of documents assigned to the cluster 
            |-> sumar total aparicions paraula / #DOCUMENTS

        Words are ordered alphabetically but you will have to use an efficient structure to
        compute the frequency of each word

        :param key:
        :param values:
        :return:
        """
        # clustID, [(docIDx,wordsListx)] -> s'han unit tots els value que tenen el mateix clust/proto
        wordsInCluster = {}
        documentsInCluster = []
        totalDocumentsInCluster = 0

        # Calcular frequencia de cada paraula i nombre total de documents associats a un cluster
        for pair in values:
            totalDocumentsInCluster += 1
            documentsInCluster.append(pair[0])
            for word in pair[1]:
                if not word in wordsInCluster:
                    wordsInCluster[word] = 1
                else:
                    wordsInCluster[word] += 1

        # Generar llista amb les paraules i el seu pes
        wordsWithWeight = []                    
        for word, freq in wordsInCluster.items():
            weight = float(freq/totalDocumentsInCluster)
            wordsWithWeight.append((word,weight))
        
        
        # Ordenar llista alfabeticament perque el dict no esta ordenat
        # Funcio lambda que donat un element retorna el primer element
        takeFirst = lambda pair: pair[0]
        wordsWithWeight = sorted(wordsWithWeight, key= takeFirst)
        documentsInCluster = sorted(documentsInCluster)

        # key/clustID, 
        yield key, (documentsInCluster,wordsWithWeight)

    def steps(self):
        return [MRStep(mapper_init=self.load_data, mapper=self.assign_prototype,
                       reducer=self.aggregate_prototype)
            ]


if __name__ == '__main__':
    MRKmeansStep.run()