import boto3
from tabulate import tabulate
from Logger import Logger
from config import AWS_REGION
import TransitGateways
import Vpc
#from access_client import AWSClient

class EC2Controller:
    #  A class for controlling interactions with the boto3 EC2  Resource and Client Interface
    INSTANCES_DISPLAY_FORMAT = '  {0}({1})  \t {2} - {3} <RegionInfo:{4}>  \t <Launched On:{5}>'

    def __init__(self, ec2_role_client, ec2client):
        # EC2Controller Constructor, assigns the ec2 Resource "ec2_role_client" and "ec2client" Client to this controller
        self.ec2_role_client = ec2_role_client
        self.ec2_client = ec2client
        self.current_interface = None
        self.role = None

    def list_instances(self):
        # List all EC2 instances
        return self.list_all_instances(self.ec2_res.instances.all())
    
    def list_all_instances(self, instances):
        count = 0
        running_instances = []
        pending_instances = []
        shutting_down_instances = []
        terminated_instances = []
        stopping_instances = []
        stopped_instances = []
        # Loop through all EC2 instances
        for instance in instances:
            instance_info = [instance.id, instance.state['Name'], instance.image_id, instance.instance_type,
                             AWS_REGION, instance.launch_time]
            if instance.state['Name'] == "running":
                running_instances.append(instance_info)
            elif instance.state['Name'] == "pending":
                pending_instances.append(instance_info)
            elif instance.state['Name'] == "shutting-down":
                shutting_down_instances.append(instance_info)
            elif instance.state['Name'] == "terminated":
                terminated_instances.append(instance_info)
            elif instance.state['Name'] == "stopping":
                stopping_instances.append(instance_info)
            elif instance.state['Name'] == "stopped":
                stopped_instances.append(instance_info)
            count += 1
        if count == 0:
            Logger.warn(self.MSG_WARN_NO_INSTANCE)
        else:
            Logger.header("<AWS EC2 Instances>")
            for running_instance in running_instances:
                Logger.info(self.INSTANCES_DISPLAY_FORMAT.format(*running_instance))
            for pending_instance in pending_instances:
                Logger.info(self.INSTANCES_DISPLAY_FORMAT.format(*pending_instance))
            for stopping_instance in stopping_instances:
                Logger.info(self.INSTANCES_DISPLAY_FORMAT.format(*stopping_instance))
            for stopped_instance in stopped_instances:
                Logger.info(self.INSTANCES_DISPLAY_FORMAT.format(*stopped_instance))
            for shutting_down_instance in shutting_down_instances:
                Logger.info(self.INSTANCES_DISPLAY_FORMAT.format(*shutting_down_instance))
            for terminated_instance in terminated_instances:
                Logger.info(self.INSTANCES_DISPLAY_FORMAT.format(*terminated_instance))
        return count
    
    def get_role_client(self, role):

        sts_client = boto3.client('sts')

        assumed_role_object=sts_client.assume_role(
            RoleArn=role,
            RoleSessionName="AssumeRoleSession1"
        )

        credentials=assumed_role_object['Credentials']

        session=boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )

        return session.client("ec2", region_name="us-gov-west-1")

    def get_tgws(self, role):
        table = []

        if role is None:
            tgws = self.ec2_client.describe_transit_gateways()['TransitGateways']
        else:
            self.ec2_role_client = self.get_role_client(role)
            tgws = self.ec2_role_client.describe_transit_gateways()['TransitGateways']
            print(f"Searching role {role}...")
   
        for tgw in tgws:
            table.append([tgw['TransitGatewayId'], tgw['TransitGatewayArn'], tgw['State'], tgw['Description'] ])

        print(tabulate(table, headers=['TransitGatewayId', 'TransitGatewayArn', 'State', 'Description'], tablefmt = 'fancy_grid')) 

    def get_vpcs(self, role):
        vpcs = []
        table = []

        if role is None:
            vpcs = self.ec2_client.describe_vpcs()['Vpcs']
        else:
            self.ec2_role_client = self.get_role_client(role)
            vpcs = self.ec2_role_client.describe_vpcs()['Vpcs']

            for vpc in vpcs:
                if 'Tags' in vpc:
                    for tag in vpc['Tags']:
                        if 'Key' in tag and tag['Key'] == 'Name':
                            table.append((vpc['CidrBlock'], vpc['VpcId'], tag['Value']))
                else:
                    table.append((vpc['CidrBlock'], vpc['VpcId'], "No Name"))

            
            print(f"Searching role {role}...")
            print(tabulate(table, headers=['CidrBlock', 'VpcId', 'Name'], tablefmt = 'fancy_grid'))
    
    def get_route_table_by_vpc(self, vpcid, role):
        print(f"Get route table for subnet: {self.current_interface['SubnetId']}")
        filters = [
            {
                'Name': 'vpc-id',
                'Values': [vpcid]
            }
        ]

        table = []
        if self.role == None:
            rtbs = self.ec2_client.describe_route_tables(Filters=filters)["RouteTables"]
        else: 
            rtbs = self.ec2_role_client.describe_route_tables(Filters=filters)["RouteTables"]

        if rtbs:
            for rtb in rtbs:
                for route in rtb['Routes']:
                    table.append([route['DestinationCidrBlock'] if 'DestinationCidrBlock' in route else "" , route['DestinationIpv6CidrBlock'] if 'DestinationIpv6CidrBlock' in route else "", route['DestinationPrefixListId'] if 'DestinationPrefixListId' in route else "", route['GatewayId'] if 'GatewayId' in route else "", route['TransitGatewayId'] if 'TransitGatewayId' in route else "", route['Origin'], route['State']])
        
                print(tabulate(table, headers=['DestinationCidrBlock', 'DestinationIpv6CidrBlock', 'DestinationPrefixListId', 'TransitGatewayId', 'GatewayId', 'Origin', 'State'], tablefmt = 'fancy_grid'))

    def get_interface(self, interfaceId, role):
        self.role = role

        filters = [
            {
                'Name': 'addresses.private-ip-address',
                'Values': [interfaceId]
            }
        ]
        
        if role is None:
            self.current_interface = self.ec2_client.describe_network_interfaces(Filters=filters)["NetworkInterfaces"][0]
        else:
            self.ec2_role_client = self.get_role_client(role)
            print(f"Searching role {role}...")
            self.current_interface = self.ec2_role_client.describe_network_interfaces(Filters=filters)["NetworkInterfaces"][0]

        if self.current_interface:
            table = []
            table.append([self.current_interface['NetworkInterfaceId'], self.current_interface['PrivateIpAddress'], self.current_interface['Ipv6Address'] if 'Ipv6Address' in self.current_interface else "Not Found", self.current_interface['Status'], self.current_interface['SubnetId'], self.current_interface['VpcId']])
        
        print(tabulate(table, headers=['NetworkInterfaceId', 'IPv4 Address', 'IPv6 Address', 'Status', 'SubnetId', 'VpcId'], tablefmt = 'fancy_grid'))
    
    def get_interface_security_groups(self):
        return self.current_interface["Groups"]
    
    def get_network_acl_by_subnet(self):

        filter = [
            {
                'Name': 'association.subnet-id',
                'Values': [self.current_interface['SubnetId']]
            }
        ]
        if self.role == None:
            nacls = self.ec2_client.describe_network_acls(Filters=filter)['NetworkAcls']
        else:
            nacls = self.ec2_role_client.describe_network_acls(Filters=filter)['NetworkAcls']
        
        table = []
        for acl in nacls:
                if "Entries" in acl:
                    for entry in acl["Entries"]:
                        toPort = entry['PortRange']['To'] if 'PortRange' in entry  else "NA"
                        fromPort = entry['PortRange']['From'] if 'PortRange' in entry  else "NA"
                        protocol = entry['Protocol'] if entry['Protocol'] != '-1' else "All"
                        table.append([entry['RuleNumber'], entry.get('CidrBlock', 'N/A'), entry.get('Ipv6CidrBlock', 'N/A'), entry['Egress'], protocol, fromPort, toPort , entry['RuleAction'], acl['NetworkAclId'], acl['VpcId']])
        
        print(tabulate(table, headers=['RuleNumber', 'IPv4 CIDR', 'IPv6 CIDR', 'Egress', 'Protocol', 'From', 'To', 'Rule Action', 'NetworkAclId', 'VpcId'], tablefmt = 'fancy_grid'))    

    def get_network_rtb(self):
        print(f"Get route table for subnet: {self.current_interface['SubnetId']}")
        filters = [
            {
                'Name': 'association.subnet-id',
                'Values': [self.current_interface['SubnetId']]
            }
        ]

        table = []
        if self.role == None:
            rtbs = self.ec2_client.describe_route_tables(Filters=filters)["RouteTables"]
        else: 
            rtbs = self.ec2_role_client.describe_route_tables(Filters=filters)["RouteTables"]

        if rtbs:
            for rtb in rtbs:
                for route in rtb['Routes']:
                    table.append(
                        [route['DestinationCidrBlock'] if 'DestinationCidrBlock' in route else "" , 
                         route['DestinationIpv6CidrBlock'] if 'DestinationIpv6CidrBlock' in route else "", 
                         route['DestinationPrefixListId'] if 'DestinationPrefixListId' in route else "", 
                         route['GatewayId'] if 'GatewayId' in route else "", 
                         route['TransitGatewayId'] if 'TransitGatewayId' in route else "", 
                         route['Origin'], 
                         route['State']])
                
                print(tabulate(table, headers=['DestinationCidrBlock', 'DestinationIpv6CidrBlock', 'DestinationPrefixListId', 'TransitGatewayId', 'GatewayId', 'Origin', 'State'], tablefmt = 'fancy_grid'))
        else:
            print(f"No route table attached to subnet {self.current_interface['SubnetId']}; Displaying default route table for { self.current_interface['VpcId'] }...")
            rtb = self.get_route_table_by_vpc(self.current_interface['VpcId'], self.role)
        
    def print_security_group_rules(self, direction, name, rules):
        table = []
        x = 1
        for rule in rules:
            if "IpRanges" in rule:
                    for cidrs in rule["IpRanges"]:
                        protocol = rule['IpProtocol'] if rule['IpProtocol'] != '-1' else "All"
                        toPort = "NA"
                        if 'ToPort' in rule:
                            if rule['ToPort'] == -1: 
                                toPort = "All"
                            else:
                                toPort = rule['ToPort']  
                        fromPort = "NA"
                        if 'FromPort' in rule:
                            if rule['FromPort'] == -1: 
                                fromPort = "All"
                            else:
                                fromPort = rule['FromPort']  

                        table.append([x, name, direction, cidrs['CidrIp'], protocol, fromPort, toPort])
                        x = x + 1

        print(tabulate(table, headers=['#', 'Name', 'Direction', 'CIDR', 'Protocol', 'From Port', 'To Port'], tablefmt = 'fancy_grid'))    
    
    def get_tgw_rtb(self, tgwId):
        filters = [
            {
                'Name': 'type',
                'Values': ['static', 'propagated']
            }
        ]

        role = TransitGateways.TGWS[tgwId]["role"]

        if role == None:
            tgw = self.ec2_client.describe_transit_gateways(TransitGatewayIds=[tgwId])["TransitGateways"][0]
            tgwrtb = tgw['Options']['AssociationDefaultRouteTableId']
            tgwrt = self.ec2_client.search_transit_gateway_routes(TransitGatewayRouteTableId=tgwrtb, Filters=filters)["Routes"]
        else:
            self.ec2_role_client = self.get_role_client(role)
            tgw = self.ec2_role_client.describe_transit_gateways(TransitGatewayIds=[tgwId])["TransitGateways"][0]
            tgwrtb = tgw['Options']['AssociationDefaultRouteTableId']
            tgwrt = self.ec2_role_client.search_transit_gateway_routes(TransitGatewayRouteTableId=tgwrtb, Filters=filters)["Routes"]
        
        table = []
        x = 1
        for route in tgwrt:
            for attach in route['TransitGatewayAttachments']:
                if attach['ResourceId'] in Vpc.vpc:
                    desc = f"{Vpc.vpc[attach['ResourceId']]['Name'] } ({attach['ResourceId']})"
                else:
                    desc = attach['ResourceId']


                table.append([x, route['DestinationCidrBlock'], desc, attach['TransitGatewayAttachmentId'], attach['ResourceType'], route['Type'], route['State']])
                x = x + 1

        print(tabulate(table, headers=['#', 'DestinationCidrBlock', 'ResourceId', 'TransitGatewayAttachmentId', 'ResourceType', 'Type', 'State'], tablefmt = 'fancy_grid'))
        
    def get_interface_security_groups_by_id(self, groupId):
        if self.role == None:
            security_groups = self.ec2_client.describe_security_groups(GroupIds=[groupId])["SecurityGroups"]
        else:
            security_groups = self.ec2_role_client.describe_security_groups(GroupIds=[groupId])["SecurityGroups"]
            
        for sg in security_groups:
                self.print_security_group_rules('Ingress', sg['GroupName'], sg['IpPermissions'])
                self.print_security_group_rules('Egress ', sg['GroupName'], sg['IpPermissionsEgress'])

    def get_all_security_groups(self, role):
        if role == None:
            return self.ec2_client.describe_security_groups()
        else:
            return self.ec2_role_client.describe_security_groups()
            
    