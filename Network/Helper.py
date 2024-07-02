from ipaddress import ip_address, ip_network, AddressValueError
import Network.CIDRAllocations

class NetworkHelper:

    def is_valid_ip(ip):
        try:
            ip_address(ip)
            return True
        except (ValueError, AddressValueError):
            return False

    def find_associated_arn(ip):
        ip = ip_address(ip)
        for entry in Network.CIDRAllocations.ngdc_cloud_allocations:
            network = ip_network(entry["CIDR"])
            if ip in network:
                return entry["ARN"]
        return None