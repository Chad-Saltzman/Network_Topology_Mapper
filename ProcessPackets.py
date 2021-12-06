# -------------------------------------------------------------------
#
#   ProcessPackets.py
#
#   Purpose: Allows for the graphing of the inputted devices 
#   and graph editing/inspecting functionality.
#
# -------------------------------------------------------------------
import time
from VisualizeGraph import VisualizeGraph
from DeviceProperties import Device

# 
def findUniqueMACs(packets):
    MAC_List = {}
    for packet in packets:
        # print(MAC_List)
        if packet["SourceMAC"] not in MAC_List:
            MAC_List[packet["SourceMAC"]] = [packets.index(packet)]
        else:
            MAC_List[packet["SourceMAC"]].append(packets.index(packet))
        if packet["DestinationMAC"] not in MAC_List:
            MAC_List[packet["DestinationMAC"]] = [packets.index(packet)]
        else:
            MAC_List[packet["DestinationMAC"]].append(packets.index(packet))
    return MAC_List


def getDevices(packets):
    devices = {}
    MACS = findUniqueMACs(packets)
    print(MACS)
    for i in range(len(MACS)):
        device_packets = []
        for index in MACS[list(MACS)[i]]:
            # print(list(MACS)[i])
            # print(sample_Packets[index])
            device_packets.append(packets[index])
        devices[list(MACS)[i]] = Device(device_packets, list(MACS)[i])

    return devices

