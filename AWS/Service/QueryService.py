class QueryService:

    def __init__(self, awsclient):
         self.awsclient = awsclient
    
    def get_vpcs(self, role):
        vpcs = []

        if role is None:
            vpcs = self.awsclient.user_client.describe_vpcs()['Vpcs']
        else:
            client = self.awsclient.get_role_client(role)
            vpcs = client.describe_vpcs()['Vpcs']
        
        return vpcs

    def get_tgws(self, role):
        tgws = []

        if role is None:
            tgws = self.awsclient.user_client.describe_transit_gateways()['TransitGateways']
        else:
            client = self.awsclient.get_role_client(role)
            tgws = client.describe_transit_gateways()['TransitGateways']
         
        return tgws
    
    def get_route_tables(self, role, filters):
        rtbs = []

        if role == None:
            rtbs = self.awsclient.user_client.describe_route_tables(Filters=filters)["RouteTables"]
        else: 
            client = self.awsclient.get_role_client(role)
            rtbs = client.describe_route_tables(Filters=filters)["RouteTables"]

        return rtbs
    
    def get_interfaces(self, role, filters):
        interfaces = []

        if role is None:
            interfaces = self.awsclient.user_client.describe_network_interfaces(Filters=filters)["NetworkInterfaces"]
        else:
            client = self.awsclient.get_role_client(role)
            interfaces = client.describe_network_interfaces(Filters=filters)["NetworkInterfaces"]
        
        return interfaces
    
    def get_network_acl(self, role, filters):
        nacls = []

        if role == None:
            nacls = self.awsclient.user_client.describe_network_acls(Filters=filters)['NetworkAcls']
        else:
            client = self.awsclient.get_role_client(role)
            nacls = client.describe_network_acls(Filters=filters)['NetworkAcls']
        
        return nacls
    
    def get_network_rtb(self, role, filters):
        rtbs = []
        if role == None:
            rtbs = self.awsclient.user_client.describe_route_tables(Filters=filters)["RouteTables"]
        else: 
            client = self.awsclient.get_role_client(role)
            rtbs = client.describe_route_tables(Filters=filters)["RouteTables"]

        if rtbs:
            return rtbs
        else:
            rtb = self.get_route_table_by_vpc(self.current_interface['VpcId'], role)
            return rtb
    
    def get_tgw_rtb(self, tgwId, role, filters):

        if role == None:
            tgw = self.awsclient.user_client.describe_transit_gateways(TransitGatewayIds=[tgwId])["TransitGateways"][0]
            tgwrtb = tgw['Options']['AssociationDefaultRouteTableId']
            return self.awsclient.user_client.search_transit_gateway_routes(TransitGatewayRouteTableId=tgwrtb, Filters=filters)["Routes"]
        else:
            client = self.awsclient.get_role_client(role)
            tgw = client.describe_transit_gateways(TransitGatewayIds=[tgwId])["TransitGateways"][0]
            tgwrtb = tgw['Options']['AssociationDefaultRouteTableId']
            return client.search_transit_gateway_routes(TransitGatewayRouteTableId=tgwrtb, Filters=filters)["Routes"]
    
   
    
    def get_security_groups_by_id(self, groupId, role):
        sgs = []

        if role == None:
            sgs = self.awsclient.user_client.describe_security_groups(GroupIds=[groupId])["SecurityGroups"]
        else:
            client = self.awsclient.get_role_client(role)
            sgs = client.describe_security_groups(GroupIds=[groupId])["SecurityGroups"]

        return sgs    
    
    def get_security_groups(self, role):
        sgs = []

        if role == None:
            sgs = self.awsclient.user_client.describe_security_groups()["SecurityGroups"]
        else:
            client = self.awsclient.get_role_client(role)
            sgs = client.describe_security_groups()["SecurityGroups"]

        return sgs    
       


