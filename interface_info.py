import wmi
class int_info:
        
    def get_network_info(interface):
        ip_info = int_info.get_IP_info(interface)
        mac_info = int_info.get_MAC_info(interface)
        mask_info = int_info.get_mask_info(interface)
        dns_info = int_info.get_dns_info(interface)
        dhcp_info = int_info.get_dhcp_info(interface)
        gw_info = int_info.get_gw_info(interface)
        return ip_info, mac_info, dns_info, gw_info, dhcp_info, mask_info 
    
    
    def get_IP_info(connection_name):
        c = wmi.WMI()

        # Iteracja przez interfejsy sieciowe
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if connection_name.lower() in interface.Description.lower():
                # Sprawdź, czy istnieje adres IP
                ip_info = interface.IPAddress
                if ip_info:
                    return ip_info[0]
                else:
                    return "Brak danych"
                
    def get_MAC_info(connection_name):
        c = wmi.WMI()

        # Iteracja przez interfejsy sieciowe
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if connection_name.lower() in interface.Description.lower():
                # Sprawdź, czy istnieje adres IP
                mac_info = interface.MACAddress
                if mac_info:
                    return mac_info
                else:
                    return "Brak danych"
    
    def get_mask_info(connection_name):
        c = wmi.WMI()

        # Iteracja przez interfejsy sieciowe
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if connection_name.lower() in interface.Description.lower():
                # Sprawdź, czy istnieje adres IP
                subnet_mask = interface.IPSubnet
                if subnet_mask:
                    return subnet_mask[0]
                else:
                    return "Brak danych"
    
    def get_dns_info(connection_name):
        c = wmi.WMI()

        # Iteracja przez interfejsy sieciowe
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if connection_name.lower() in interface.Description.lower():
                # Sprawdź, czy istnieje adres DNS
                dns_servers = interface.DNSServerSearchOrder
                if dns_servers:
                    return f"{', '.join(dns_servers)}"
                else:
                    return "Brak danych"
    
    def get_dhcp_info(connection_name):
        c = wmi.WMI()
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if connection_name.lower() in interface.Description.lower():
                    # Sprawdź, czy interfejs korzysta z DHCP
                if interface.DHCPEnabled:
                    return interface.DHCPServer
                else:
                    "Brak danych"
                    
                    
    def get_gw_info(connection_name):
        c = wmi.WMI()
        for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            if connection_name.lower() in interface.Description.lower():
                    # Sprawdź, czy interfejs korzysta z DHCP
                if interface.DefaultIPGateway:
                    return interface.DefaultIPGateway[0]
                else:
                    "Brak danych"