from ipaddress import ip_address, ip_network, AddressValueError
import Vpc
import roles
from AWS.Service.QueryService import QueryService


class NetworkHelper:

    def __init__(self, queryservice):
        # init
        self.queryservice = queryservice

    def is_valid_ip(self, ip):
        try:
            ip_address(ip)
            return True
        except (ValueError, AddressValueError):
            return False

    def find_associated_arn(self, ip):
        ip = ip_address(ip)
        for key, value in roles.AWS_ROLES.items():
            vpcs = self.queryservice.get_vpcs(key)
            for vpc in vpcs:
                network = ip_network(vpc['CidrBlock'])
                if ip in network:
                    return key
    
    def list_transit_gateways(self):
        tgws_list = {}
        for key, value in roles.AWS_ROLES.items():
            tgws = self.queryservice.get_tgws(key)
            for tgw in tgws:
                tgws_list[tgw['TransitGatewayId']] = { 'description': tgw['Description'] }
        
        return tgws_list
