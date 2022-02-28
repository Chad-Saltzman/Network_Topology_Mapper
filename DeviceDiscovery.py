import netmiko
from netmiko import Netmiko
import fsm_paths
from getpass import getpass
import ipaddress
import re
import sys
import time
import textfsm
import requests
import json 


# Switch models start with "ws"
# firewall models have "ASA" or "ISA" or "SM" in them
# Router models are only numbers or have "ASR" or "ISR" in them
# Endpoints cannot be distinguished from one another
# Phones will show up in cdp neighbors



class Device:
    
    def __init__(self, IP):
        self.IP = IP 
        self.mac_address = "" 
        self.model = ""
        self.neighbors = []
        self.interfaces = {}
        self.device_type = ""


    def getDeviceType(self):
        if self.model:
            if self.model.startswith("ws") or re.match(r'N\dK', self.model) or "vios_l2" in self.model:
                self.device_type = "Switch"
            elif "ASA" in self.model or "ISA" in self.model or "SM" in self.model:
                self.device_type = "Firewall"
            elif "Phone" in self.model:
                self.device_type = "Phone"
            else:
                self.device_type = "Router"

    def getNeighbors(self):
        pass 

            

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

    def __repr__(self):
        return f"{self.IP=}\n{self.mac_address=}\n{self.model=}\n{self.neighbors=}\n{self.interfaces=}\n{self.device_type=}\n\n"

class Port:

    def __init__(self, port_name = "", IP = "", destination_ip = "", destination_port = ""):
        self.port_name = port_name
        self.IP = IP
        self.vlans = []
        self.speed = ""
        self.duplex = ""
        self.mode = ""
        self.description = ""
        self.type = ""
        self.destination_port = ""
        self.destination_IP = ""

def deviceDiscoveryMain():
    hostname_set = set()
    total_time = 0
    average_time = 0
    successfully_porocessed_devices = 0
    not_able_to_process_devices = 0

    devices_dict = {}

    # Collect credentials
    username = input("Enter username: ") or "netdiscover"
    password = getpass("Enter password: ") or "password"
    ip_address = input("IP Address of Seed Device: ") or "192.168.0.118"
    completed_devices = 0   
    # Loop through our devices as long as we have more
    discovered_devices = {ip_address} 
    devices = [ip_address]    
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
                continue
            if ip_address not in devices_dict:
                devices_dict[ip_address] = Device(ip_address)
            hostname = net_connect.find_prompt()[:-1]  # Finds the hostname of the device
            hostname_set.add(hostname)

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
                    

            except Exception as e:
                print(f"Failed to find neighbors for {ip_address}")
                print(e)
                sys.exit()
                    
            try:
                command = "show mac address-table"
                output = net_connect.send_command(command)
                mac_addresses = []
                if "Invalid input detected" in output:
                    command = "show ip arp"
                    output = net_connect.send_command(command)
                    with open(fsm_paths.show_ip_arp_fsm_path) as template:
                        fsm = textfsm.TextFSM(template)
                    macs = fsm.ParseText(output)
                    for mac in macs:
                        if mac[1] not in devices:
                            mac_addresses.append([mac[3]])
                            mac_addresses[-1].extend([mac[5]])
                else:
                    with open(fsm_paths.show_mac_address_table_fsm_path) as template:
                        fsm = textfsm.TextFSM(template)
                    macs = fsm.ParseText(output)
                    for mac in macs:
                        if mac[3] in ports_with_neighbors:
                            continue
                        mac_addresses.append([mac[0]])
                        mac_addresses[-1].extend([mac[3]])
            except:
                print(f"Failed to find mac addresses for {ip_address}")

            completed_devices += 1
            print(mac_addresses)

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
                # print(msg)
    for ip in devices_dict:
        devices_dict[ip].getDeviceType()
    print(devices_dict)

if __name__ == '__main__':
    deviceDiscoveryMain()