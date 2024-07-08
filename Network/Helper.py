from ipaddress import ip_address, ip_network, AddressValueError
import Vpc

class NetworkHelper:

    def is_valid_ip(ip):
        try:
            ip_address(ip)
            return True
        except (ValueError, AddressValueError):
            return False
   
    def find_associated_arn(ip):
        ip = ip_address(ip)
        for vpc in Vpc.vpc.items():
            for entry in vpc[1]["CidrBlock"]:
                network = ip_network(entry)
                if ip in network:
                    return vpc[1]["role"]
        return None