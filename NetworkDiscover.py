import nmap
class NetworkScanner:

    def scan_network(ip_range):
        nm = nmap.PortScanner()
        nm.scan(hosts=ip_range, arguments='-sn')

        devices = []
        for host in nm.all_hosts():
            hostname = nm[host].hostname() if nm[host].hostname() else 'N/A'
            if 'mac' in nm[host]['addresses']:
                mac_address = nm[host]['addresses']['mac']
            else:
                mac_address = 'N/A'

            devices.append({'ip': host,'hostname': hostname, 'mac': mac_address})

        return devices
        
        