import netmiko
from netmiko import Netmiko
import website.python.fsm_paths as fsm_paths
from getpass import getpass
import ipaddress
import re
import sys
import time
import textfsm
import requests
import json 
import math


# Switch models start with "ws"
# firewall models have "ASA" or "ISA" or "SM" in them
# Router models are only numbers or have "ASR" or "ISR" in them
# Endpoints cannot be distinguished from one another
# Phones will show up in cdp neighbors

class Device:
    
    def __init__(self, IP):
        self.IP = IP 
        self.hostname = None
        self.local_mac_address = list()
        self.model = "None"
        self.neighbors = []
        self.interfaces = {}
        self.device_type = "None"

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
                    sort_keys=True, indent=4)


    def __repr__(self):
        
        return self.toJSON().replace("'", '"')

    def getDeviceType(self):
        if self.model:
            if self.model.startswith("ws") or re.match(r'N\dK', self.model) or "vios_l2" in self.model:
                self.device_type = "Switch"
            elif "ASA" in self.model or "ISA" in self.model or "SM" in self.model:
                self.device_type = "Firewall"
            elif "Phone" in self.model:
                self.device_type = "IPPhone"
            elif self.hostname == None:
                self.device_type = "Desktop"
            else:
                self.device_type = "Router"

    # Creates a list of device neighbors based on device mac address table and/or arp table
    def getNeighbors(self):
        for interface in self.interfaces:
            if self.interfaces[interface].macs:  # Checks if macs were found in the mac address table
                for mac in self.interfaces[interface].macs:
                    self.neighbors.append(mac)  
            elif self.interfaces[interface].destination_IP in IP_to_Hostname:   # Checks if neighboring interfaces were found that are not local interface IP addresses
                self.neighbors.append(getHostnameFromIP(self.interfaces[interface].destination_IP, IP_to_Hostname))
            else:
                self.neighbors.append(self.interfaces[interface].destination_IP)
        print(self.neighbors)

    def removeDuplicateNeighbors(self, IP_to_hostname):
        unique_neighbors = []
        for neighbor in self.neighbors:
            if neighbor not in unique_neighbors:
                if neighbor in IP_to_hostname:
                    neighbor = IP_to_hostname[neighbor]
                unique_neighbors.append(neighbor)

        

        self.neighbors = unique_neighbors


    # Gets the device vendor based on the OUI of the MAC Address
    def getVendor(self):

        try: # Attempts to connect to first API
            response = requests.get(f"https://api.macvendors.com/{self.mac_address}", timeout=1)  
            vendor = response.text
            time.sleep(0.5)
            if "errors" in vendor:
                raise ValueError
            if type(vendor) == str:
                return vendor
            else:
                 return "None"
        except :  # First API Call failed. Trying second API
            try:
                response = requests.get(f"http://www.macvendorlookup.com/api/v2/{self.mac_address}/json", timeout=1)
                json_response = json.loads(response.text)
                vendor = json_response[0]['company']
                time.sleep(0.5)
                if type(vendor) == str:
                    return vendor
                else:
                    return "None"
            except:
                return "None"

    

class Port:

    def __init__(self, port_name = "", IP = "", destination_ip = "", destination_port = ""):
        self.port_name = port_name
        self.IP = IP
        self.vlans = []
        self.speed = ""
        self.duplex = ""
        self.macs = []
        self.mode = ""
        self.description = ""
        self.type = ""
        self.destination_port = ""
        self.destination_IP = ""

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
                    sort_keys=True, indent=4)

    def __repr__(self):
        return self.toJSON().replace("'", '"')


# Gets node details in json format to build graph in javascript
def getNodes(devices, color = ""):
    if not devices:
        return
    list_of_nodes = []
    # DIR = "../website/static/images/"
    # router_img = "NetDiscover_Icon_Router_V1.png"
    # firewall_img = "NetDiscover_Icon_FireWall_V1.png"
    # switch_img = "NetDiscover_Icon_Switch_V1.png"
    # endpoint_img = "NetDiscover_Icon_Desktop_V1.png"
    for device in devices:
        node_properties = {
            'id' : devices[device].hostname if devices[device].hostname else devices[device].IP,
            'group' : devices[device].device_type + color if devices[device].device_type else "Desktop" + color,
            'title' : devices[device].IP,
            # 'title' : f"{devices[device].IP} {devices[device].neighbors" 
            'label' : devices[device].hostname if devices[device].hostname else devices[device].IP,
            'shape' : 'circularImage', 
            'size' : 20,
            'smooth' : False
        }
        list_of_nodes.append(node_properties)
    return list_of_nodes

# Gets edge details in json format to build graph in javascript
def getEdges(devices):
    if not devices:
        return
    list_of_edges = []
    edges_to_skip = []
    for device in devices:
        for neighbor in devices[device].neighbors:
            edge_properties = {
                'from' : devices[device].hostname if devices[device].hostname else devices[device].IP,
                'to' : neighbor
            }
            edges_to_skip.append(
                {
                    'from' : neighbor,
                    'to' : devices[device].hostname if devices[device].hostname else devices[device].IP,
                }
            )

            if edge_properties not in edges_to_skip:
                list_of_edges.append(edge_properties)
    return list_of_edges

# Organizes Subnets from most specific to least specific (e.g. /24 is more specific than /16)
def sortSubnets(subnet_dict):
    sorted_subnets = {}
    list_of_subnets = list(subnet_dict)
    list_of_subnets.sort(reverse = True, key=getIPPrefix)

    for subnet in list_of_subnets:
        sorted_subnets[subnet] = {}

    for subnet in list_of_subnets:
        for user_pass in subnet_dict[subnet]:
            sorted_subnets[subnet][user_pass] =  subnet_dict[subnet][user_pass]

    return sorted_subnets

# Gets the prefix value from the IP Subnet  (192.168.10.10/24)
def getIPPrefix(subnet):
    # print(subnet)
    return int(subnet.split('/')[1])

# Gets the device hostname from the IP Address
def getHostnameFromIP(IP_address, IP_address_to_hostname_dict):
    return IP_address_to_hostname_dict[IP_address]

# Gurantees that host bits are not set 
def verifySubnets(subnets_dict):
    verified_subnets = {}
    for subnet in subnets_dict:
        prefix = int(subnet.split('/')[1])
        network = subnet.split('/')[0]   # IP Address section of IP Subnet
        octet_to_check = math.floor(prefix / 8)  # Calculates which octet needs to be checked
        if octet_to_check == 4:
            continue 
        octet_value = int(network.split('.')[octet_to_check])
        network_bits = prefix % 8
        if 2**(8 - network_bits) % octet_value  != 0:  
            new_octet_value = octet_value - (octet_value % 2**(8 - network_bits) )
            verified_subnets[subnet.replace(octet_value, new_octet_value)] = subnets_dict[subnet]
        else:
            verified_subnets[subnet] = subnets_dict[subnet]
    return verified_subnets

IP_to_Hostname = {}

def deviceDiscovery(ip_address, auth_data_dict):
    IP_to_Hostname = {}
    hostname_set = set()
    total_time = 0
    average_time = 0
    auth_data_dict = sortSubnets(auth_data_dict)
    successfully_porocessed_devices = 0
    not_able_to_process_devices = 0
    IP_map = {}
    devices_dict = {}
    devices = []
    start_time = time.time()  

    # Collect credentials
    # username = input("Enter username: ") or "netdiscover"
    # password = getpass("Enter password: ") or "password"
    # ip_address = input("IP Address of Seed Device: ") or "192.168.111.129"
    completed_devices = 0   
    devices.append(ip_address)  
    while completed_devices < len(devices):
        total_time = time.time() - start_time
        try:
            ip_address = devices[completed_devices]  # Gets the most recent IP address to log into.
            if completed_devices > 0:  # Gives a general output after each device
                average_time = round(total_time / completed_devices, 2)
                estimated_time = round(average_time * len(devices), 2)
                remaining_time_estimate = round(estimated_time - total_time, 2)
                msg = (f"Some Statistics:\n"
                       f" - Processed: {completed_devices}/{len(devices)} devices\n"
                       f" - Could not process: {not_able_to_process_devices} devices\n"
                       f" - On average it takes {average_time} seconds per device\n"
                       f" - Remaining: {len(devices) - completed_devices } devices\n"
                       f" - Estimated Time to completion: {time.strftime('%H hours %M minutes %S seconds', time.gmtime(remaining_time_estimate))}")
                print(msg)

            create_IP = ipaddress.ip_address(ip_address)
            for subnet in auth_data_dict:  # Loops through subnets provided in credentials page
                create_subnet = ipaddress.ip_network(subnet)
                if create_IP in create_subnet: 
                    username = auth_data_dict[subnet]['username']
                    password = auth_data_dict[subnet]['password']
                    break

            msg = f"\nNow Discovering: {ip_address}\n"
            print(msg)
            # Creates dictionary of device data needed to SSH to it.
            device = {
                        "host": ip_address, 
                        "username": username,
                        "password": password,
                        "secret": "password",
                        "device_type": "cisco_ios"
                    }
            try:
                net_connect = Netmiko(**device)     # Establishes connection to device 

            except netmiko.ssh_exception.NetmikoTimeoutException:
                msg = f"Unable to SSH to {ip_address}, skipping."
                print(msg)

                not_able_to_process_devices += 1
                completed_devices += 1

                continue
            
            if ip_address not in devices_dict:
                devices_dict[ip_address] = Device(ip_address)

            hostname = net_connect.find_prompt()[:-1]  # Finds the hostname of the device
            hostname_set.add(hostname)
            devices_dict[ip_address].hostname = hostname 
            IP_to_Hostname[ip_address] = hostname
            # if "(config" in net_connect.find_prompt():
            #     net_connect.send_command("end")
            # elif ">" in net_connect.find_prompt():
            #     net_connect.enable()
            command = "show version"
            """  Example output
            Cisco IOS Software, vios_l2 Software (vios_l2-ADVENTERPRISEK9-M), Version 15.2(CML_NIGHTLY_20190423)FLO_DSGS7, EARLY DEP
            LOYMENT DEVELOPMENT BUILD, synced to  V152_6_0_81_E
            Technical Support: http://www.cisco.com/techsupport
            Copyright (c) 1986-2019 by Cisco Systems, Inc.
            Compiled Tue 23-Apr-19 04:48 by mmen


            ROM: Bootstrap program is IOSv

            Switch1 uptime is 1 hour, 50 minutes
            System returned to ROM by reload
            System image file is "flash0:/vios_l2-adventerprisek9-m"
            Last reload reason: Unknown reason
            """
            try:
                output = net_connect.send_command(command)
                model_result = re.search(r"Cisco IOS Software, (?P<model>(\S*\-?)*)", output)
                if model_result:
                    # host_report.model = device_data.model = result.group('model') 
                    devices_dict[ip_address].model = model_result.group('model') # Retrieves the device model type
                    msg = f"model of {ip_address} is {devices_dict[ip_address].model}"
                else:
                    msg = f"unable to get model for {ip_address}"
            
                serial_result = re.match(r"System\s*serial\s*number\s*:\s*(?P<serial>.+)", output, re.MULTILINE)
                if serial_result:
                    devices_dict[ip_address].serial = serial_result.group('serial')  # Retrieves the system serial number
                    msg = f"serial of {ip_address} is {devices_dict[ip_address].serial}"
                else:
                    msg = f"unable to get serial for {ip_address}"
            except:
                print(f"Failed to find model and serial for {ip_address}")

            try:
                command = "show ip interface brief"
                """ Example output
                Interface                  IP-Address      OK? Method Status                Protocol
                GigabitEthernet0/0         192.168.15.3    YES DHCP   up                    up
                GigabitEthernet0/1         20.0.0.1        YES NVRAM  up                    up
                GigabitEthernet0/2         20.0.0.5        YES NVRAM  up                    up
                GigabitEthernet0/3         unassigned      YES NVRAM  administratively down down
                """
                output = net_connect.send_command(command)
                with open(fsm_paths.show_ip_interface_brief_ios_fsm_path) as template:
                            fsm = textfsm.TextFSM(template)
                interface_brief_result = fsm.ParseText(output)
                for interface in interface_brief_result:
                    if interface[1] != "unassigned" and 'vlan' not in interface[0].lower() and 'port-channel' not in interface[0].lower():  # Gets only physical interface IP addresses.
                        if interface[0] not in devices_dict[ip_address].interfaces:
                            devices_dict[ip_address].interfaces[interface[0]] = Port(IP=interface[1])
                        if interface[1] != ip_address:
                            IP_map[interface[1]] = ip_address

            except:
                print(f"Failed to find layer3 interfaces for {ip_address}")
            
            try:
                command = "show cdp neighbors detail"
                """ Example output
                Device ID: Router3.netdiscover
                Entry address(es):
                IP address: 20.0.0.6
                Platform: Cisco ,  Capabilities: Router Source-Route-Bridge
                Interface: GigabitEthernet0/2,  Port ID (outgoing port): GigabitEthernet0/2
                Holdtime : 130 sec

                Version :
                Cisco IOS Software, IOSv Software (VIOS-ADVENTERPRISEK9-M), Version 15.9(3)M2, RELEASE SOFTWARE (fc1)
                Technical Support: http://www.cisco.com/techsupport
                Copyright (c) 1986-2020 by Cisco Systems, Inc.
                Compiled Tue 28-Jul-20 07:09 by prod_rel_team

                advertisement version: 2
                Management address(es):
                IP address: 20.0.0.6

                -------------------------
                """
                output = net_connect.send_command(command)
                with open(fsm_paths.cdp_neighbors_details_ios_fsm_path) as template:
                    fsm = textfsm.TextFSM(template)
                neighbors = fsm.ParseText(output)
                
                for neighbor in neighbors:
                    hostname = re.sub(r'\.\S+', '', neighbor[0])
                    if not hostname in hostname_set and neighbor[1] not in devices:
                        devices.append(neighbor[1])  # Adds new found device IP
                        if neighbor[1] not in devices_dict:
                            devices_dict[neighbor[1]] = Device(neighbor[1])
                            devices_dict[neighbor[1]].model = neighbor[2]
                    if neighbor[3] not in devices_dict[ip_address].interfaces:
                        devices_dict[ip_address].interfaces[neighbor[3]] = Port(port_name=neighbor[3], destination_ip=neighbor[1], destination_port=neighbor[4])
                    if neighbor[1] in IP_map and IP_map[neighbor[1]] not in devices_dict[ip_address].neighbors and IP_map[neighbor[1]] != ip_address:
                        if IP_map[neighbor[1]] in IP_to_Hostname:
                            devices_dict[ip_address].neighbors.append(IP_to_Hostname[IP_map[neighbor[1]]])
                        else:
                            devices_dict[ip_address].neighbors.append(IP_map[neighbor[1]])
                    elif neighbor[1] not in IP_map and neighbor[1] not in devices_dict[ip_address].neighbors and neighbor[1] != ip_address:
                        if neighbor[1] in IP_to_Hostname:
                            devices_dict[ip_address].neighbors.append(IP_to_Hostname[neighbor[1]])
                        else:
                            devices_dict[ip_address].neighbors.append(neighbor[1])
                    

            except Exception as e:
                print(f"Failed to find neighbors for {ip_address}")
                print(e)
                sys.exit()

            try:
                command = "show interface"
                """ Example output
                GigabitEthernet0/0 is up, line protocol is up
                Hardware is iGbE, address is 5000.0001.0000 (bia 5000.0001.0000)
                Internet address is 192.168.15.3/24
                MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
                    reliability 129/255, txload 1/255, rxload 1/255
                Encapsulation ARPA, loopback not set
                Keepalive set (10 sec)
                Auto Duplex, Auto Speed, link type is auto, media type is RJ45
                output flow-control is unsupported, input flow-control is unsupported
                ARP type: ARPA, ARP Timeout 04:00:00
                Last input 00:00:01, output 00:00:02, output hang never
                Last clearing of "show interface" counters never
                Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
                Queueing strategy: fifo
                Output queue: 0/40 (size/max)
                5 minute input rate 0 bits/sec, 0 packets/sec
                5 minute output rate 0 bits/sec, 0 packets/sec
                    13782 packets input, 1025132 bytes, 0 no buffer
                    Received 4547 broadcasts (0 IP multicasts)
                    4115 runts, 0 giants, 0 throttles
                    4115 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
                    0 watchdog, 0 multicast, 0 pause input
     """
                output = net_connect.send_command(command)
                with open (fsm_paths.show_interface_fsm_path) as template:
                    fsm = textfsm.TextFSM(template)
                interfaces = fsm.ParseText(output)

                for interface in interfaces:
                    if interface[1] != 'up' or interface[2] != 'up':
                        continue
                    if interface[4]:
                        if interface[0] not in devices_dict[ip_address].interfaces:
                            devices_dict[ip_address].interfaces[interface[0]] = Port(port_name = interface[0])
                        devices_dict[ip_address].local_mac_address.append(interface[4])
                        if interface[7]:
                            devices_dict[ip_address].interfaces[interface[0]].IP = interface[7]
            except Exception as e:
                print("failed to find interface details")
                print(e)
                sys.exit()
      
            try:
                command = "show ip arp"
                """ Example output
                Protocol  Address          Age (min)  Hardware Addr   Type   Interface
                Internet  20.0.0.1                -   5000.0001.0001  ARPA   GigabitEthernet0/1
                Internet  20.0.0.2              113   5000.0002.0001  ARPA   GigabitEthernet0/1
                Internet  20.0.0.5                -   5000.0001.0002  ARPA   GigabitEthernet0/2
                Internet  20.0.0.6              113   5000.0003.0002  ARPA   GigabitEthernet0/2
                Internet  192.168.15.1            0   58d9.d5fc.d590  ARPA   GigabitEthernet0/0
                Internet  192.168.15.3            -   5000.0001.0000  ARPA   GigabitEthernet0/0
                Internet  192.168.15.5            0   000c.2930.d06e  ARPA   GigabitEthernet0/0
                Internet  192.168.15.178          6   a051.0b38.256a  ARPA   GigabitEthernet0/0
                """
                output = net_connect.send_command(command)
                        
                with open(fsm_paths.show_ip_arp_fsm_path) as template:
                    fsm = textfsm.TextFSM(template)
                macs = fsm.ParseText(output)
                for mac in macs:
                    if "Router" in devices_dict[ip_address].hostname:
                        break
                    if mac[1] in IP_map and IP_map[mac[1]] not in devices_dict[ip_address].neighbors and IP_map[mac[1]] != ip_address:
                        if IP_map[mac[1]] in IP_to_Hostname:
                            devices_dict[ip_address].neighbors.append(IP_to_Hostname[IP_map[mac[1]]])
                        else:
                            devices_dict[ip_address].neighbors.append(IP_map[mac[1]])
                    elif mac[1] not in IP_map and mac[1] not in devices_dict[ip_address].neighbors and mac[1] != ip_address:
                        if mac[1] in IP_to_Hostname:
                            devices_dict[ip_address].neighbors.append(IP_to_Hostname[mac[1]])
                        else:
                            devices_dict[ip_address].neighbors.append(mac[1])
                        if mac[1] not in devices:
                            devices_dict[mac[1]] = Device(mac[1])

                    # if mac[5] not in devices_dict[ip_address].interfaces:
                    #     devices_dict[ip_address].interfaces[mac[5]] = Port(port_name = mac[5])
                    # devices_dict[ip_address].interfaces[mac[5]].macs.append(mac[3])

        
            except Exception as e:
                print(f"Failed to find neighbor IP's for {ip_address}")
                print(e)
                sys.exit()
            completed_devices += 1

        except Exception as e:
            print(e)
            completed_devices += 1
    successfully_porocessed_devices += 1
    if completed_devices > 0:  # Gives a general output after each device
                average_time = round(total_time / completed_devices, 2)
                estimated_time = round(average_time * len(devices), 2)
                remaining_time_estimate = round(estimated_time - total_time, 2)
                remaining_time_estimate = 0 if len(devices) == 0 else remaining_time_estimate
                msg = (f"Some Statistics:\n"
                       f" - Processed: {completed_devices}/{len(devices)} devices\n"
                       f" - Could not process: {not_able_to_process_devices} devices\n"
                       f" - On average it takes {average_time} seconds per device\n"
                       f" - Remaining: {len(devices) - completed_devices } devices\n"
                       f" - Estimated Time to completion: {time.strftime('%H hours %M minutes %S seconds', time.gmtime(remaining_time_estimate))}")
                print(msg)
    for ip in devices_dict:
        devices_dict[ip].getDeviceType()
        devices_dict[ip].removeDuplicateNeighbors(IP_to_Hostname)
    return devices_dict

def DiscoveryMain(IP_address, subnets):

    device_dict = deviceDiscovery(IP_address, subnets)

    nodes = getNodes(device_dict)
    print(nodes)
    edges = getEdges(device_dict)
    print(edges)
    node_data = json.dumps(nodes)
    edge_data = json.dumps(edges)


    with open("node.json", 'w') as temp_file:   
        temp_file.write(f"node data: {node_data}")

    with open("edge.json", 'w') as temp_file:   
        temp_file.write(f"edge data: {edge_data}")
    
    return True 

def exportDeviceData( devices, file_name = "", write_true = True):
    if write_true:
        with open(file_name, 'w') as exported_file:
            json_data = str(devices)
            exported_file.write()
            print("exporting")
    else:
        return str(devices).replace("'", '"')

# Takes json file as input and recreates all device objects from the JSON Object
def importDeviceData(file_name = "", json_string = ""):
    devices_dict = {}
    if file_name:
        import_file = open(file_name)
        print("importing")
    if json_string:
        import_data = json.loads(json_string.replace("'", '"'))
    else:
        import_data = json.loads(import_file.read())
    for device_IP in import_data:
        devices_dict[device_IP] = Device(device_IP)
        for attribute in import_data[device_IP]:
            if attribute == 'interfaces':
                for interface in import_data[device_IP][attribute]:
                    devices_dict[device_IP].interfaces[interface] = Port(port_name=interface)
                    for interface_attribute in import_data[device_IP][attribute][interface]:
                        if type(import_data[device_IP][attribute][interface][interface_attribute]) == str:
                            exec('devices_dict[device_IP].interfaces[interface].%s = "%s"' % (interface_attribute, import_data[device_IP][attribute][interface][interface_attribute]))  # Adds string values 
                        else:
                            exec('devices_dict[device_IP].interfaces[interface].%s = %s' % (interface_attribute, import_data[device_IP][attribute][interface][interface_attribute]))  # Adds any non string datatype/datastructure

            else:
                if type(import_data[device_IP][attribute]) == str:
                    exec('devices_dict[device_IP].%s = "%s"' % (attribute, import_data[device_IP][attribute]))
                else:
                    exec('devices_dict[device_IP].%s = %s' % (attribute, import_data[device_IP][attribute]))
        if file_name:
            import_file.close()

    return devices_dict 
    