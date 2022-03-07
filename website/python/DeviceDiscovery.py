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
        self.hostname = ""
        self.local_mac_address = set()
        self.model = ""
        self.neighbors = []
        self.interfaces = {}
        self.device_type = ""

    def __repr__(self):
        device_dict = {}
        device_dict["IP"] = self.IP 
        device_dict['hostname'] = self.hostname 
        device_dict['local_mac_address'] = list(self.local_mac_address)
        device_dict['model'] = self.model 
        device_dict['neighbors'] = self.neighbors
        device_dict['interfaces'] = str(self.interfaces)
        device_dict['device_type'] = self.device_type 
        
        return json.dumps(device_dict)


    def getDeviceType(self):
        if self.model:
            if self.model.startswith("ws") or re.match(r'N\dK', self.model) or "vios_l2" in self.model:
                self.device_type = "switch"
            elif "ASA" in self.model or "ISA" in self.model or "SM" in self.model:
                self.device_type = "firewalls"
            elif "Phone" in self.model:
                self.device_type = "ipphone"
            else:
                self.device_type = "routers"

    def getNeighbors(self):
        for interface in self.interfaces:
            if self.interfaces[interface].macs:
                for mac in self.interfaces[interface].macs:
                    self.neighbors.append(mac)
            else:
                self.neighbors.append(self.interfaces[interface].destination_IP)
            

    def getVendor(self):
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
            response = requests.get(f"https://api.macvendors.com/{self.mac_address}", timeout=1)
            vendor = response.text 
            time.sleep(0.5)
            if type(vendor) == str:
                return response.text
            else:
                 return "None"

    

class Port:

    def __init__(self, port_name = "", IP = "", destination_ip = "", destination_port = ""):
        self.port_name = port_name
        self.IP = IP
        self.vlans = []
        self.speed = ""
        self.duplex = ""
        self.macs = set()
        self.mode = ""
        self.description = ""
        self.type = ""
        self.destination_port = ""
        self.destination_IP = ""

    def __repr__(self):
        port_dict = {}
        port_dict['port_name'] = self.port_name
        port_dict['IP'] = self.IP
        port_dict['vlans'] = self.vlans
        port_dict['speed'] = self.speed
        port_dict['duplex'] = self.duplex
        port_dict['macs'] = list(self.macs)
        port_dict['mode'] = self.mode
        port_dict['description'] = self.description
        port_dict['type'] = self.type
        port_dict['destination_port'] = self.destination_port
        port_dict['destination_IP'] = self.destination_IP
        return json.dumps(port_dict)

def getNodes(devices):
    list_of_nodes = []
    # DIR = "../website/static/images/"
    # router_img = "NetDiscover_Icon_Router_V1.png"
    # firewall_img = "NetDiscover_Icon_FireWall_V1.png"
    # switch_img = "NetDiscover_Icon_Switch_V1.png"
    # endpoint_img = "NetDiscover_Icon_Desktop_V1.png"
    for device in devices:
        node_properties = {
            'id' : devices[device].IP,
            'group' : devices[device].device_type,
            'title' : devices[device].IP,
            'shape' : 'circularImage', 
            'size' : 20,
            'smooth' : False
        }
        list_of_nodes.append(node_properties)
    return list_of_nodes

def getEdges(devices):
    list_of_edges = []

    for device in devices:
        for neighbor in devices[device].neighbors:
            edge_properties = {
                'from' : devices[device].IP,
                'to' : neighbor
            }
            list_of_edges.append(edge_properties)
    return list_of_edges

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

def getIPPrefix(subnet):
    return int(subnet.split('/')[1])

# Gurantees that host bits are not set 
def verifySubnets(subnets_dict):
    verified_subnets = {}
    for subnet in subnets_dict:
        prefix = int(subnet.split('/')[1])
        network = subnet.split('/')[0]
        octet_to_check = math.floor(prefix / 8)
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

def deviceDiscovery(ip_address, auth_data_dict):
    hostname_set = set()
    total_time = 0
    average_time = 0
    auth_data_dict = sortSubnets(auth_data_dict)
    successfully_porocessed_devices = 0
    not_able_to_process_devices = 0
    IP_map = {}
    devices_dict = {}

    # Collect credentials
    # username = input("Enter username: ") or "netdiscover"
    # password = getpass("Enter password: ") or "password"
    # ip_address = input("IP Address of Seed Device: ") or "192.168.111.129"
    completed_devices = 0   
    # Loop through our devices as long as we have more
    discovered_devices = {ip_address} 
    devices = [ip_address]    
    unique_macs = set()
    while completed_devices < len(devices):
        try:
            start = time.time()  
            ip_address = devices[completed_devices]  # Gets the most recent IP address to log into.
            ports_with_neighbors = []
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
            for subnet in auth_data_dict:
                create_subnet = ipaddress.ip_network(subnet)
                if create_IP in create_subnet:
                    username = auth_data_dict[subnet]['username']
                    password = auth_data_dict[subnet]['password']
                    break
            msg = f"\nNow Discovering: {ip_address}\n"
            print(msg)
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
                # host_report.skip(
                #     msg,
                #     exc_info=True,
                # )
                # exception_log(exceptions_log_filename, msg)
                not_able_to_process_devices += 1
                completed_devices += 1

                continue
            
            if ip_address not in devices_dict:
                devices_dict[ip_address] = Device(ip_address)
            hostname = net_connect.find_prompt()[:-1]  # Finds the hostname of the device
            hostname_set.add(hostname)
            devices_dict[ip_address].hostname = hostname 
            # if "(config" in net_connect.find_prompt():
            #     net_connect.send_command("end")
            # elif ">" in net_connect.find_prompt():
            #     net_connect.enable()
            command = "show version"
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
                        devices_dict[ip_address].neighbors.append(IP_map[neighbor[1]])
                    elif neighbor[1] not in IP_map and neighbor[1] not in devices_dict[ip_address].neighbors and neighbor[1] != ip_address:
                        devices_dict[ip_address].neighbors.append(neighbor[1])
                    

            except Exception as e:
                print(f"Failed to find neighbors for {ip_address}")
                print(e)
                sys.exit()

            try:
                command = "show interface"
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
                        devices_dict[ip_address].local_mac_address.add(interface[4])
                        if interface[7]:
                            devices_dict[ip_address].interfaces[interface[0]].IP = interface[7]
            except Exception as e:
                print("failed to find interface details")
                print(e)
                sys.exit()
      
            try:
                command = "show ip arp"
                output = net_connect.send_command(command)
                    
                with open(fsm_paths.show_ip_arp_fsm_path) as template:
                    fsm = textfsm.TextFSM(template)
                macs = fsm.ParseText(output)
                for mac in macs:
                    if mac[1] in IP_map and IP_map[mac[1]] not in devices_dict[ip_address].neighbors and IP_map[mac[1]] != ip_address:
                        devices_dict[ip_address].neighbors.append(IP_map[mac[1]])
                    elif mac[1] not in IP_map and mac[1] not in devices_dict[ip_address].neighbors and mac[1] != ip_address:
                        devices_dict[ip_address].neighbors.append(mac[1])
                        if mac[1] not in devices:
                            devices_dict[mac[1]] = Device(mac[1])

                    # if mac[5] not in devices_dict[ip_address].interfaces:
                    #     devices_dict[ip_address].interfaces[mac[5]] = Port(port_name = mac[5])
                    # devices_dict[ip_address].interfaces[mac[5]].macs.add(mac[3])

        
            except Exception as e:
                print(f"Failed to find neighbor IP's for {ip_address}")
                print(e)
                sys.exit()
            completed_devices += 1

        except Exception as e:
            print(e)
            completed_devices += 1
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
    for ip in devices_dict:
        devices_dict[ip].getDeviceType()
    return devices_dict

def DiscoveryMain(IP_address, subnets):

    device_dict = deviceDiscovery(IP_address, subnets)

    nodes = getNodes(device_dict)
    edges = getEdges(device_dict)
    node_data = json.dumps(nodes)
    edge_data = json.dumps(edges)


    with open("node.json", 'w') as temp_file:   
        temp_file.write(f"node data: {node_data}")

    with open("edge.json", 'w') as temp_file:   
        temp_file.write(f"edge data: {edge_data}")
    
    return True 

def exportDeviceData(file_name, devices):
    with open(file_name, 'w') as exported_file:
        json_data = str(devices).replace("'", '"').strip('("').strip('")').replace('\\','').replace('"{', "{").replace('}"', '}')
        exported_file.write(json_data)
        print("exporting")

def importDeviceData(file_name):
    devices_dict = {}
    with open(file_name, 'r') as import_file:
        print("importing")
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

                #print(devices_dict[device_IP].attribute)
            else:
                if type(import_data[device_IP][attribute]) == str:
                    exec('devices_dict[device_IP].%s = "%s"' % (attribute, import_data[device_IP][attribute]))
                else:
                    exec('devices_dict[device_IP].%s = %s' % (attribute, import_data[device_IP][attribute]))
    #print(devices_dict)
    return devices_dict 
    
if __name__ == '__main__':
    import os 
    #print(os.getcwd())
    # Sample set of subnets to test 
    subnets = {"192.0.0.0/8": {'username' : 'netdiscover', 'password' : 'password'}, "192.168.0.0/16": {'username' : 'netdiscover', 'password' : 'password'}, "192.168.0.0/24": {'username' : 'netdiscover', 'password' : 'password'}, "192.168.0.0/32": {'username' : 'netdiscover', 'password' : 'password'}}

    devices_dict = deviceDiscovery("192.168.111.129", subnets)
    exportDeviceData("test.json", devices_dict)
    importDeviceData("test.json")
    nodes = getNodes(devices_dict)
    edges = getEdges(devices_dict)
    node_data = json.dumps(nodes)
    edge_data = json.dumps(edges)
    with open("node.txt", 'w') as temp_file:   
        temp_file.write(f"node data: {node_data}")

    with open("edge.txt", 'w') as temp_file:   
        temp_file.write(f"edge data: {edge_data}")

    ############# FINISH SCAN 