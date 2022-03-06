#
#   Name: Carlos Dye
#   Document: Compare.py
#   Purpose: Comparison between old and new toplogies 
#

compTopology = []
missTopology = []

class Compare:
    # topology1: old topo
    # topology2: new topo
    def compareTopologies(topology1, topology2):

        for device1 in topology1:
            foundIP = False
            for device2 in topology2:
                if device1 == device2:
                    foundIP = True
            if(foundIP):
                compTopology.append(device1)
            else:
                missTopology.append(device1)

    def getFinalCompareValid():
        return compTopology
    
    def getFinalCompareMiss():
        return missTopology

    

