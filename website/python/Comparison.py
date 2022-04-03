#
#   Name: Carlos Dye
#   Document: Compare.py
#   Purpose: Comparison between old and new toplogies 
#

# topology1: old topo
# topology2: new topo
def compareTopologies(topology1, topology2):
    TopologyChanges = {
        'compTopology' : {},
        'missTopology' : {},
        'newTopology' : {},
    }

    for device1 in topology1: # iterate through Topo1 devices
        foundDevice = False # flag if a match is found
        for device2 in topology2: # iterate through Topo2 devices
            if topology1[device1].hostname and topology2[device2].hostname: # check to see if hostnames exist for both devices
                if topology1[device1].hostname == topology2[device2].hostname: # first check to see if two devices match by hostname
                    foundDevice = True # flag to true if match found
                    break # no need to continue searching for a match since we know it exists 
            else: # next check to see if two devices match by IP address 
                if topology1[device1].IP == topology2[device2].IP: # IP address compare check
                    foundDevice = True # flag to true if match found 
                    break # no need to continue 
        if foundDevice: # if flag ends in true then 
            TopologyChanges['compTopology'][topology1[device1].IP] = topology1[device1] # add to compTopology since both Topos share same node 
        else: # if flag ends in false then 
            TopologyChanges['missTopology'][topology1[device1].IP] = topology1[device1] # add to missTopology since both Topos do not share node 

    for device2 in topology2: # iterate through Topo1 devices
        foundDevice = False # flag if a match is found
        for device1 in topology1: # iterate through Topo2 devices
            if topology2[device2].hostname and topology1[device1].hostname: # check to see if hostnames exist for both devices
                if topology2[device2].hostname == topology1[device1].hostname: # first check to see if two devices match by hostname
                    foundDevice = True # flag to true if match found
                    break # no need to continue searching for a match since we know it exists 
            else: # next check to see if two devices match by IP address 
                if topology2[device2].IP == topology1[device1].IP: # IP address compare check
                    foundDevice = True # flag to true if match found 
                    break # no need to continue 

        if not foundDevice:
            TopologyChanges['newTopology'][topology2[device2].IP] = topology2[device2]
    
    return TopologyChanges


# def combineDevices(comparison_dict):
#     final_comparison_dict = {}
#     for group in comparison_dict: 
#         for device in comparison_dict[group]:
#             final_comparison_dict[comparison_dict[group][device].IP] = comparison_dict[group][device]


#     return final_comparison_dict    
    