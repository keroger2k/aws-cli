#!/usr/bin/env python3
from menu import Menu
from Logger import Logger
from Network import Helper
from config import AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import os
import roles
import Resources
import EC2
import TransitGateways
from AWS.Client.AccessClient import AWSClient
from AWS.Service.QueryService import QueryService

# String constants
STR_HEADER = "--------------------------------------------------------------------"
STR_FOOTER = "--------------------------------------------------------------------"
STR_PROMPT = ">>"
STR_SUFFIX = ": "
STR_WINDOWS = "windows"
STR_LINUX = "linux"
STR_CWD = "[CWD:'{}']"
KEY_AWS_KEY = "aws_key"
KEY_AWS_SECRET = "aws_secret"

class AwsCli:

    def __init__(self):
        # init
        self.logged_in = False
        self.username = None
        self.passwdDict = dict()
        self.ec2_role_client = None
        self.ec2_client = None
        self.ec2_cont = None
        
        # -------------EC2-------------
        # Options of EC2 Menu
        self.ec2_menu_options = [
            ("List all instances", self.ec2_list),
            ("Go back", Menu.CLOSE)
        ]
        # EC2 Menu
        self.ec2_menu = Menu(
            options=self.ec2_menu_options,
            title="\n[EC2 Menu]",
            auto_clear=False
        )

        # -------------Search IP-------------
        # Options of Search IP Menu
        self.search_ip_menu_options = [
            ("List all Security Groups", self.search_ip_list_sg),
            ("Display Network ACL", self.search_ip_list_nacl),
            ("Display Routing Table", self.search_ip_display_rtb),
            ("Display TGW Routing Table", self.search_ip_display_tgw_rtb),
            ("Go back", Menu.CLOSE)
        ]

        # Search IP Menu
        self.search_ip_menu = Menu(
            options=self.search_ip_menu_options,
            title="\n[Search IP Menu]",
            auto_clear=False
        )

        # -------------Main Menu-------------
        # Options of Main Menu
        self.main_menu_options = [
            ("EC2 Instances", self.ec2_menu.open),
            ("Search IP", self.search_ip),
            ("Search IP in SG", self.search_ip_in_sg),
            ("Display All VPC Info", self.display_all_vpc_info),
            ("Display TGWs", self.display_all_tgw_info),
            ("Display TGWs Routing Table", self.search_ip_list_tgw),
            ("Go back", Menu.CLOSE)
        ]
        # Main Menu
        self.main_menu = Menu(
            title="\n[Main Menu]",
            message="",
            auto_clear=False)

        self.main_menu.set_prompt(STR_PROMPT)
        self.main_menu.set_options(self.main_menu_options)

    def ec2_controller(self):
        # get EC2 Controller
        if self.ec2_cont is None:
            resource = Resources.Resource(AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
            awsclient = AWSClient(resource)
            queryservice = QueryService(awsclient)
            self.ec2_cont = EC2.EC2Controller(queryservice)
        return self.ec2_cont

    def ec2_list(self):
        # Get the EC2 list
        cont = self.ec2_controller()
        Logger.header(STR_HEADER)
        cont.list_instances()
        Logger.header(STR_FOOTER)

    def search_ip_list_nacl(self):
        # Get the EC2 list
        cont = self.ec2_controller()
        Logger.header(STR_HEADER)
        sgs = cont.get_network_acl_by_subnet()
        Logger.header(STR_FOOTER)

    def search_ip_display_rtb(self):
        # Get the EC2 list
        cont = self.ec2_controller()
        Logger.header(STR_HEADER)
        sgs = cont.get_network_rtb()
        Logger.header(STR_FOOTER)

    def search_ip_display_tgw_rtb(self):
        #assign local
        cont = self.ec2_controller()
                    
        while True:
            Logger.header(STR_HEADER)
            tgwId = input("Enter the TGW ID: ")
            cont.get_tgw_rtb(tgwId)
            d = input("Press any key to continue...")
            self.search_ip_menu.open()   
    
    def search_ip_list_sg(self):
        # Get the EC2 list
        cont = self.ec2_controller()
        Logger.header(STR_HEADER)
        sgs = cont.get_interface_security_groups()
        sgs_menu_options = []
        
        sgs_menu = Menu(
            title="[Security Groups Menu]",
            auto_clear=False
        )

        if sgs is not None:
            for sg in sgs: 
                sgs_menu_options.append((f"{sg['GroupName']}: {sg['GroupId']}", lambda id = sg['GroupId']: cont.get_interface_security_groups_by_id(id))) 
        
        sgs_menu_options.append(("Go back", Menu.CLOSE))
        sgs_menu.set_options(sgs_menu_options)
        sgs_menu.open()

        Logger.header(STR_FOOTER)

    def search_ip_list_tgw(self):
        # Get the EC2 list
        cont = self.ec2_controller()
        Logger.header(STR_HEADER)
        tgw_menu_options = []
        
        tgw_menu = Menu(
            title="[Transit Gateways Menu]",
            auto_clear=False
        )

        for key in TransitGateways.TGWS: 
            tgw_menu_options.append((f"{key}: {TransitGateways.TGWS[key]["description"]}", lambda id = key: cont.get_tgw_rtb(id))) 
    
        tgw_menu_options.append(("Go back", Menu.CLOSE))
        tgw_menu.set_options(tgw_menu_options)
        tgw_menu.open()

        Logger.header(STR_FOOTER)

    def setting_enable_color_menu(self):
        # Enable color Menu
        if self.logged_in:
            Logger.enable_color()

    def setting_disable_color_menu(self):
        # Enable color Menu to make simple
        if self.logged_in:
            Logger.disable_color()

    def display_all_vpc_info(self):
        cont = self.ec2_controller()
        Logger.header(STR_HEADER)
        cont.get_vpcs(None)
        for value in roles.AWS_ROLES:
            cont.get_vpcs(value)
        Logger.header(STR_FOOTER)
    
    def display_all_tgw_info(self):
        cont = self.ec2_controller()
        Logger.header(STR_HEADER)
        cont.get_tgws(None)
        for value in roles.AWS_ROLES:
            cont.get_tgws(value)
        Logger.header(STR_FOOTER)

    def search_ip(self):
        #assign local
        cont = self.ec2_controller()
                    
        while True:
            Logger.header(STR_HEADER)
            ip_address = input("Input the IP address to search: ")
            if Helper.NetworkHelper.is_valid_ip(ip_address):
                arn = Helper.NetworkHelper.find_associated_arn(ip_address)
                if arn is None:
                    cont.get_interface(ip_address, None)
                else:
                    cont.get_interface(ip_address, arn)
                self.search_ip_menu.open()   
            else:
                Logger.err(f"Invalid IP Address: {ip_address}")

    def search_ip_in_sg(self):
        #assign local
        cont = self.ec2_controller()
                    
        Logger.header(STR_HEADER)
        ip_address = input("Input the IP address to search: ")
        sec_groups = cont.get_all_security_groups(None)
        print("Checking default acount....")
        for security_group in sec_groups['SecurityGroups']:
            for rule in security_group['IpPermissions']:
                for ip_range in rule['IpRanges']:
                    if (ip_range['CidrIp'] == ip_address):
                        print(f"Found rule for {ip_address}: in security group: {security_group['GroupName']} ({security_group['GroupId']})")

        for value in roles.AWS_ROLES:
            print(f"Checking {value} acount....")
            sec_groups = cont.get_all_security_groups(value)
            for security_group in sec_groups['SecurityGroups']:
                for rule in security_group['IpPermissions']:
                    for ip_range in rule['IpRanges']:
                        if (ip_range['CidrIp'] == ip_address):
                            print(f"Found rule for {ip_address}: in security group: {security_group['GroupName']} ({security_group['GroupId']})")

    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        # Main method
        self.clear_console()
        #self.resource = Resources.Resource(AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        #aws_clients = AWSClient(self.resource)
        #self.ec2_client = aws_clients.get_user_client()
        self.main_menu.open()


if __name__ == "__main__":
    try:
        AwsCli().run()
    except KeyboardInterrupt as error:
        Logger.err(str(error))
    except Exception as e:
        Logger.err(str(e))
